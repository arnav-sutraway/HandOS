from __future__ import annotations

import argparse
import queue
import signal
import sys
import threading
import time
from typing import Optional

import cv2
import numpy as np
from mediapipe.tasks.python.vision.hand_landmarker import HandLandmarksConnections

from handos.actions.mouse import MouseController
from handos.data import VisionPacket
from handos.gestures.pinch import PinchStateMachine, pinch_ratio
from handos.signal.dead_zone import DeadZone
from handos.signal.kalman import CursorKalman2D
from handos.vision.capture import CameraThread
from handos.vision.preprocessor import landmark_to_screen
from handos.vision.worker import VisionThread

INDEX_TIP = 8


def _draw_hand_overlay(frame_bgr: np.ndarray, landmarks: np.ndarray) -> None:
    h, w = frame_bgr.shape[:2]

    def pt(i: int) -> tuple[int, int]:
        return int(landmarks[i, 0] * w), int(landmarks[i, 1] * h)

    for conn in HandLandmarksConnections.HAND_CONNECTIONS:
        cv2.line(frame_bgr, pt(conn.start), pt(conn.end), (0, 200, 0), 2)
    for i in range(21):
        cv2.circle(frame_bgr, pt(i), 3, (0, 0, 255), -1)
    cv2.circle(frame_bgr, pt(INDEX_TIP), 6, (255, 255, 0), 2)


def _debug_print(enabled: bool, message: str) -> None:
    if enabled:
        print(message, flush=True)


def _parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="HandOS Phase 1: index cursor + pinch click")
    p.add_argument("--camera", type=int, default=0, help="OpenCV camera index")
    p.add_argument("--no-preview", action="store_true", help="Disable OpenCV preview window")
    p.add_argument("--dead-zone", type=float, default=5.0, help="Dead zone in pixels")
    p.add_argument("--pinch-threshold", type=float, default=0.30, help="Pinch ratio threshold (smaller = tighter pinch)")
    p.add_argument("--pinch-activate-frames", type=int, default=3, help="Consecutive pinch frames to confirm")
    p.add_argument("--pinch-release-frames", type=int, default=3, help="Consecutive open frames to release pinch")
    p.add_argument(
        "--pinch-click-hold-seconds",
        type=float,
        default=0.0,
        help="Stable pinch hold time before clicking once (default 0.0 = immediate click)",
    )
    p.add_argument("--debug-pinch", action="store_true", help="Print pinch/click debug events to the terminal")
    p.add_argument("--kalman-dt", type=float, default=1.0 / 30.0, help="Initial Kalman dt seconds")
    p.add_argument("--width", type=int, default=640, help="Capture width")
    p.add_argument("--height", type=int, default=480, help="Capture height")
    return p.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> int:
    args = _parse_args(argv)

    frame_queue: queue.Queue = queue.Queue(maxsize=2)
    vision_queue: queue.Queue[VisionPacket] = queue.Queue(maxsize=5)

    stop = threading.Event()

    def handle_sig(_sig, _frame) -> None:
        stop.set()

    signal.signal(signal.SIGINT, handle_sig)
    if sys.platform == "win32":
        signal.signal(signal.SIGBREAK, handle_sig)  # type: ignore[attr-defined]

    include_preview = not args.no_preview
    camera = CameraThread(
        frame_queue,
        device_index=args.camera,
        width=args.width,
        height=args.height,
    )
    vision = VisionThread(frame_queue, vision_queue, include_frame_copy=include_preview)

    camera.start()
    if not camera.first_frame.wait(timeout=8.0):
        print("HandOS: timed out waiting for camera frames. Check device index and permissions.", file=sys.stderr)
        camera.stop()
        camera.join(timeout=2.0)
        return 1

    vision.start()

    mouse = MouseController()
    kf = CursorKalman2D(dt=args.kalman_dt)
    dz = DeadZone(threshold_px=args.dead_zone)
    pinch_sm = PinchStateMachine(
        activate_frames=args.pinch_activate_frames,
        release_frames=args.pinch_release_frames,
        click_hold_seconds=args.pinch_click_hold_seconds,
    )

    last_t = time.perf_counter()
    last_debug_t = last_t
    window = "HandOS (q or Esc to quit)"
    last_click_status = ""
    last_click_status_t = 0.0

    try:
        while not stop.is_set():
            try:
                pkt = vision_queue.get(timeout=0.5)
            except queue.Empty:
                if include_preview and cv2.waitKey(1) & 0xFF in (27, ord("q")):
                    break
                continue

            now = time.perf_counter()
            dt = now - last_t
            last_t = now
            kf.set_dt(dt if dt > 1e-4 else args.kalman_dt)

            if pkt.landmarks is None:
                pinch_sm.reset()
                kf.reset()
                dz.reset()
                last_click_status = ""
                if include_preview and pkt.frame_bgr is not None:
                    vis = cv2.flip(pkt.frame_bgr, 1)
                    cv2.putText(vis, "No hand", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                    cv2.imshow(window, vis)
                    if cv2.waitKey(1) & 0xFF in (27, ord("q")):
                        break
                continue

            lm = pkt.landmarks
            ix, iy = landmark_to_screen(
                lm[INDEX_TIP, 0:2],
                mouse.screen_w,
                mouse.screen_h,
                mirror_x=True,
            )
            sx, sy = kf.step(ix, iy)
            moved = dz.apply(sx, sy)
            if moved is not None:
                mx, my = moved
                mouse.move_to(mx, my)

            pinch_value, is_pinch = pinch_ratio(lm, threshold=args.pinch_threshold)
            stable_pinch, click_triggered = pinch_sm.update(is_pinch, dt)
            if now - last_debug_t >= 0.25:
                _debug_print(
                    args.debug_pinch,
                    (
                        f"[pinch] ratio={pinch_value:.3f} threshold={args.pinch_threshold:.3f} "
                        f"raw={is_pinch} stable={stable_pinch}"
                    ),
                )
                last_debug_t = now
            if click_triggered:
                sent_native = mouse.click_left()
                last_click_status = "CLICK" if sent_native else "CLICK_FALLBACK"
                last_click_status_t = now
                _debug_print(
                    args.debug_pinch,
                    (
                        f"[click] triggered ratio={pinch_value:.3f} "
                        f"hold={args.pinch_click_hold_seconds:.2f}s status={last_click_status}"
                    ),
                )

            if include_preview and pkt.frame_bgr is not None:
                vis = pkt.frame_bgr.copy()
                _draw_hand_overlay(vis, lm)
                vis = cv2.flip(vis, 1)
                label = "PINCH" if stable_pinch else "MOVE"
                cv2.putText(vis, label, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 255), 2)
                cv2.putText(
                    vis,
                    f"ratio {pinch_value:.3f} / {args.pinch_threshold:.3f}",
                    (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (255, 255, 255),
                    2,
                )
                if args.pinch_click_hold_seconds > 0.0 and stable_pinch:
                    hold_progress = min(1.0, pinch_sm.held_seconds / args.pinch_click_hold_seconds)
                    cv2.putText(
                        vis,
                        f"hold {pinch_sm.held_seconds:.2f}s / {args.pinch_click_hold_seconds:.2f}s",
                        (10, 90),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (0, 255, 255),
                        2,
                    )
                    cv2.rectangle(vis, (10, 102), (210, 118), (90, 90, 90), 1)
                    cv2.rectangle(vis, (10, 102), (10 + int(200 * hold_progress), 118), (0, 255, 255), -1)
                if last_click_status and (now - last_click_status_t) <= 1.5:
                    cv2.putText(
                        vis,
                        last_click_status,
                        (10, 145),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.8,
                        (0, 255, 0),
                        2,
                    )
                elif (now - last_click_status_t) > 1.5:
                    last_click_status = ""
                cv2.imshow(window, vis)
                key = cv2.waitKey(1) & 0xFF
                if key in (27, ord("q")):
                    break
    finally:
        stop.set()
        camera.stop()
        vision.stop()
        camera.join(timeout=2.0)
        vision.join(timeout=3.0)
        if include_preview:
            try:
                cv2.destroyAllWindows()
            except cv2.error:
                pass

    return 0
