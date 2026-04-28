from __future__ import annotations

import queue
import threading
import time
from dataclasses import dataclass
from typing import Callable, Optional

import numpy as np

from handos.actions.mouse import MouseController
from handos.core.config import EngineConfig
from handos.core.events import EngineEvent
from handos.data import VisionPacket
from handos.gestures.pinch import PinchStateMachine, pinch_ratio
from handos.signal.dead_zone import DeadZone
from handos.signal.kalman import CursorKalman2D
from handos.vision.capture import CameraThread
from handos.vision.preprocessor import landmark_to_screen
from handos.vision.worker import VisionThread

INDEX_TIP = 8


@dataclass
class EngineSnapshot:
    """Latest processed state, suitable for GUI or preview rendering."""

    frame_bgr: Optional[np.ndarray] = None
    landmarks: Optional[np.ndarray] = None
    handedness: str = ""
    handedness_score: float = 0.0
    pinch_value: float = 0.0
    stable_pinch: bool = False
    click_status: str = ""
    click_status_age_seconds: float = 0.0
    held_seconds: float = 0.0
    timestamp: float = 0.0


class GestureEngine:
    """Reusable runtime service for camera capture, inference, and pointer control."""

    def __init__(
        self,
        config: EngineConfig,
        event_callback: Optional[Callable[[EngineEvent], None]] = None,
    ) -> None:
        self.config = config
        self._event_callback = event_callback
        self._frame_queue: "queue.Queue[np.ndarray]" = queue.Queue(maxsize=2)
        self._vision_queue: "queue.Queue[VisionPacket]" = queue.Queue(maxsize=5)
        self._stop = threading.Event()
        self._loop_thread: Optional[threading.Thread] = None
        self._camera: Optional[CameraThread] = None
        self._vision: Optional[VisionThread] = None
        self._snapshot = EngineSnapshot()
        self._snapshot_lock = threading.Lock()
        self._latest_error: Optional[str] = None
        self._hand_present = False
        self._last_click_status = ""
        self._last_click_status_t = 0.0

        self._mouse = MouseController() if config.enable_mouse_control else None
        self._kf = CursorKalman2D(dt=config.kalman_dt)
        self._dz = DeadZone(threshold_px=config.dead_zone)
        self._pinch_sm = PinchStateMachine(
            activate_frames=config.pinch_activate_frames,
            release_frames=config.pinch_release_frames,
            click_hold_seconds=config.pinch_click_hold_seconds,
        )

    @property
    def latest_error(self) -> Optional[str]:
        return self._latest_error

    @property
    def is_running(self) -> bool:
        return self._loop_thread is not None and self._loop_thread.is_alive()

    def start(self) -> None:
        if self.is_running:
            return

        self._stop.clear()
        self._latest_error = None
        self._camera = CameraThread(
            self._frame_queue,
            device_index=self.config.camera,
            width=self.config.width,
            height=self.config.height,
        )
        self._vision = VisionThread(
            self._frame_queue,
            self._vision_queue,
            include_frame_copy=self.config.include_frame_copy,
        )

        self._camera.start()
        if not self._camera.first_frame.wait(timeout=self.config.camera_timeout_seconds):
            self._latest_error = (
                "Timed out waiting for camera frames. Check device index and permissions."
            )
            self._emit("camera_error", self._latest_error, camera=self.config.camera)
            self._camera.stop()
            self._camera.join(timeout=2.0)
            self._camera = None
            raise RuntimeError(self._latest_error)

        self._vision.start()
        self._loop_thread = threading.Thread(
            target=self._run_loop,
            name="HandOS-Engine",
            daemon=True,
        )
        self._loop_thread.start()
        self._emit("engine_started", "Gesture engine started.", camera=self.config.camera)

    def stop(self) -> None:
        self._stop.set()
        if self._camera is not None:
            self._camera.stop()
        if self._vision is not None:
            self._vision.stop()

    def join(self, timeout: Optional[float] = None) -> None:
        if self._loop_thread is not None:
            self._loop_thread.join(timeout=timeout)

    def wait_until_stopped(self) -> None:
        self.join()

    def get_snapshot(self) -> EngineSnapshot:
        with self._snapshot_lock:
            return EngineSnapshot(
                frame_bgr=None if self._snapshot.frame_bgr is None else self._snapshot.frame_bgr.copy(),
                landmarks=None if self._snapshot.landmarks is None else self._snapshot.landmarks.copy(),
                handedness=self._snapshot.handedness,
                handedness_score=self._snapshot.handedness_score,
                pinch_value=self._snapshot.pinch_value,
                stable_pinch=self._snapshot.stable_pinch,
                click_status=self._snapshot.click_status,
                click_status_age_seconds=self._snapshot.click_status_age_seconds,
                held_seconds=self._snapshot.held_seconds,
                timestamp=self._snapshot.timestamp,
            )

    def _emit(self, kind: str, message: str, **payload: object) -> None:
        if self._event_callback is None:
            return
        self._event_callback(EngineEvent(kind=kind, message=message, payload=dict(payload)))

    def _set_snapshot(self, snapshot: EngineSnapshot) -> None:
        with self._snapshot_lock:
            self._snapshot = snapshot

    def _run_loop(self) -> None:
        last_t = time.perf_counter()
        last_debug_t = last_t

        try:
            while not self._stop.is_set():
                try:
                    pkt = self._vision_queue.get(timeout=0.5)
                except queue.Empty:
                    continue

                now = time.perf_counter()
                dt = now - last_t
                last_t = now
                self._kf.set_dt(dt if dt > 1e-4 else self.config.kalman_dt)

                if pkt.landmarks is None:
                    if self._hand_present:
                        self._emit("hand_lost", "Hand tracking lost.")
                    self._hand_present = False
                    self._pinch_sm.reset()
                    self._kf.reset()
                    self._dz.reset()
                    self._last_click_status = ""
                    self._set_snapshot(
                        EngineSnapshot(
                            frame_bgr=pkt.frame_bgr,
                            landmarks=None,
                            handedness=pkt.handedness,
                            handedness_score=pkt.handedness_score,
                            timestamp=time.time(),
                        )
                    )
                    continue

                if not self._hand_present:
                    self._emit("hand_detected", "Hand detected.", handedness=pkt.handedness)
                self._hand_present = True

                lm = pkt.landmarks
                pinch_value, stable_pinch = self._process_landmarks(lm, dt, now, last_debug_t)
                if now - last_debug_t >= 0.25:
                    last_debug_t = now
                click_status_age = max(0.0, now - self._last_click_status_t)

                snapshot = EngineSnapshot(
                    frame_bgr=pkt.frame_bgr,
                    landmarks=lm,
                    handedness=pkt.handedness,
                    handedness_score=pkt.handedness_score,
                    pinch_value=pinch_value,
                    stable_pinch=stable_pinch,
                    click_status=self._last_click_status if click_status_age <= 1.5 else "",
                    click_status_age_seconds=click_status_age,
                    held_seconds=self._pinch_sm.held_seconds,
                    timestamp=time.time(),
                )
                if click_status_age > 1.5:
                    self._last_click_status = ""
                self._set_snapshot(snapshot)
        finally:
            self._teardown()

    def _process_landmarks(
        self,
        landmarks: np.ndarray,
        dt: float,
        now: float,
        last_debug_t: float,
    ) -> tuple[float, bool]:
        if self._mouse is not None:
            ix, iy = landmark_to_screen(
                landmarks[INDEX_TIP, 0:2],
                self._mouse.screen_w,
                self._mouse.screen_h,
                mirror_x=True,
            )
            sx, sy = self._kf.step(ix, iy)
            moved = self._dz.apply(sx, sy)
            if moved is not None:
                mx, my = moved
                self._mouse.move_to(mx, my)

        pinch_value, is_pinch = pinch_ratio(landmarks, threshold=self.config.pinch_threshold)
        stable_pinch, click_triggered = self._pinch_sm.update(is_pinch, dt)

        if self.config.debug_pinch and now - last_debug_t >= 0.25:
            self._emit(
                "pinch_debug",
                "Pinch telemetry updated.",
                ratio=round(pinch_value, 4),
                threshold=self.config.pinch_threshold,
                stable=stable_pinch,
                raw=is_pinch,
            )

        if click_triggered:
            sent_native = True
            if self._mouse is not None:
                sent_native = self._mouse.click_left()
            self._last_click_status = "CLICK" if sent_native else "CLICK_FALLBACK"
            self._last_click_status_t = now
            self._emit(
                "click_triggered",
                "Click gesture fired.",
                ratio=round(pinch_value, 4),
                hold_seconds=self.config.pinch_click_hold_seconds,
                status=self._last_click_status,
            )

        return pinch_value, stable_pinch

    def _teardown(self) -> None:
        self._stop.set()
        if self._camera is not None:
            self._camera.stop()
        if self._vision is not None:
            self._vision.stop()
        if self._camera is not None:
            self._camera.join(timeout=2.0)
        if self._vision is not None:
            self._vision.join(timeout=3.0)
        self._camera = None
        self._vision = None
        self._emit("engine_stopped", "Gesture engine stopped.")
