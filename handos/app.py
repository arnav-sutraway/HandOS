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


def _parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="HandOS Phase 1: index cursor + pinch click")
    p.add_argument("--camera", type=int, default=0, help="OpenCV camera index")
    p.add_argument("--no-preview", action="store_true", help="Disable OpenCV preview window")
    p.add_argument("--dead-zone", type=float, default=5.0, help="Dead zone in pixels")
    p.add_argument("--pinch-threshold", type=float, default=0.05, help="Pinch ratio threshold (smaller = tighter pinch)")
    p.add_argument("--pinch-activate-frames", type=int, default=3, help="Consecutive pinch frames to confirm")
    p.add_argument("--pinch-release-frames", type=int, default=3, help="Consecutive open frames to release pinch")
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
    )

    last_t = time.perf_counter()
    window = "HandOS (q or Esc to quit)"

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

            _, is_pinch = pinch_ratio(lm, threshold=args.pinch_threshold)
            _stable, click_edge = pinch_sm.update(is_pinch)
            if click_edge:
                mouse.click_left()

            if include_preview and pkt.frame_bgr is not None:
                vis = pkt.frame_bgr.copy()
                _draw_hand_overlay(vis, lm)
                vis = cv2.flip(vis, 1)
                label = "PINCH" if _stable else "MOVE"
                cv2.putText(vis, label, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 255), 2)
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
