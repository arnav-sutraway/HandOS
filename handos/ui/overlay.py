from __future__ import annotations

import cv2
import numpy as np
from mediapipe.tasks.python.vision.hand_landmarker import HandLandmarksConnections

from handos.core.engine import EngineSnapshot
from handos.core.config import EngineConfig

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


def render_preview(snapshot: EngineSnapshot, config: EngineConfig) -> np.ndarray | None:
    if snapshot.frame_bgr is None:
        return None

    if snapshot.landmarks is None:
        vis = cv2.flip(snapshot.frame_bgr, 1)
        cv2.putText(vis, "No hand", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        return vis

    vis = snapshot.frame_bgr.copy()
    _draw_hand_overlay(vis, snapshot.landmarks)
    vis = cv2.flip(vis, 1)

    label = "PINCH" if snapshot.stable_pinch else "MOVE"
    cv2.putText(vis, label, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 255), 2)
    cv2.putText(
        vis,
        f"ratio {snapshot.pinch_value:.3f} / {config.pinch_threshold:.3f}",
        (10, 60),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2,
    )
    if config.pinch_click_hold_seconds > 0.0 and snapshot.stable_pinch:
        hold_progress = min(1.0, snapshot.held_seconds / config.pinch_click_hold_seconds)
        cv2.putText(
            vis,
            f"hold {snapshot.held_seconds:.2f}s / {config.pinch_click_hold_seconds:.2f}s",
            (10, 90),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 255),
            2,
        )
        cv2.rectangle(vis, (10, 102), (210, 118), (90, 90, 90), 1)
        cv2.rectangle(vis, (10, 102), (10 + int(200 * hold_progress), 118), (0, 255, 255), -1)
    if snapshot.click_status:
        cv2.putText(
            vis,
            snapshot.click_status,
            (10, 145),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2,
        )
    return vis
