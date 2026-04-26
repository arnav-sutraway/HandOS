import numpy as np

from handos.vision.preprocessor import hand_scale


def pinch_ratio(landmarks: np.ndarray, threshold: float = 0.05) -> tuple[float, bool]:
    """
    Normalized distance between thumb tip (4) and index tip (8).
    Returns (ratio, is_pinch) where ratio = dist / hand_size.
    """
    thumb_tip = landmarks[4, :3]
    index_tip = landmarks[8, :3]
    dist = float(np.linalg.norm(thumb_tip - index_tip))
    scale = hand_scale(landmarks)
    ratio = dist / scale
    return ratio, ratio < threshold


class PinchStateMachine:
    """Debounced pinch open/closed with rising-edge click notification."""

    def __init__(self, activate_frames: int = 3, release_frames: int = 3) -> None:
        self.activate_frames = activate_frames
        self.release_frames = release_frames
        self._high = 0
        self._low = 0
        self._pinched = False

    def reset(self) -> None:
        self._high = 0
        self._low = 0
        self._pinched = False

    def update(self, is_pinch_raw: bool) -> tuple[bool, bool]:
        """
        Returns (pinched_stable, click_rising_edge).
        click_rising_edge is True on the first frame pinch becomes stably active.
        """
        click_edge = False
        if is_pinch_raw:
            self._high += 1
            self._low = 0
        else:
            self._low += 1
            self._high = 0

        if not self._pinched and self._high >= self.activate_frames:
            self._pinched = True
            click_edge = True
        elif self._pinched and self._low >= self.release_frames:
            self._pinched = False

        return self._pinched, click_edge
