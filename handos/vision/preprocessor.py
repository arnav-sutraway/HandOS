from typing import Tuple

import numpy as np


def landmark_to_screen(
    landmark_xy: np.ndarray,
    screen_width: int,
    screen_height: int,
    mirror_x: bool = True,
) -> Tuple[float, float]:
    """
    Map a normalized MediaPipe landmark (x,y in ~[0,1]) to pixel coordinates.
    MediaPipe x is normalized by frame width, y by frame height.
    """
    x = float(landmark_xy[0])
    y = float(landmark_xy[1])
    if mirror_x:
        x = 1.0 - x
    sx = x * float(screen_width)
    sy = y * float(screen_height)
    return sx, sy


def hand_scale(landmarks: np.ndarray) -> float:
    """Euclidean distance wrist (0) → middle MCP (9), lower bound for normalization."""
    wrist = landmarks[0, :3]
    middle_mcp = landmarks[9, :3]
    d = float(np.linalg.norm(wrist - middle_mcp))
    return max(d, 1e-6)
