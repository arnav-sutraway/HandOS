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
    multiplier = 1.4  # Optional scaling factor to allow reaching screen edges
    x = float(landmark_xy[0])
    y = float(landmark_xy[1])
    if mirror_x:
        x = 1.0 - x
    sx = x * float(screen_width) * multiplier
    sy = y * float(screen_height) * multiplier
    return sx, sy


def hand_scale(landmarks: np.ndarray) -> float:
    """
    Stable 2D palm scale for gesture normalization.

    Uses wrist (0), index MCP (5), and pinky MCP (17) in image space to avoid
    z-axis noise and to better match the apparent hand size in the preview.
    """
    wrist = landmarks[0, :2]
    index_mcp = landmarks[5, :2]
    pinky_mcp = landmarks[17, :2]
    distances = (
        float(np.linalg.norm(wrist - index_mcp)),
        float(np.linalg.norm(wrist - pinky_mcp)),
        float(np.linalg.norm(index_mcp - pinky_mcp)),
    )
    return max(sum(distances) / len(distances), 1e-6)
