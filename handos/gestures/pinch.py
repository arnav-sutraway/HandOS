import numpy as np

from handos.vision.preprocessor import hand_scale

THUMB_TIP = 4
INDEX_TIP = 8
MIDDLE_TIP = 12


def pinch_ratio(
    landmarks: np.ndarray,
    *,
    finger_tip_index: int = INDEX_TIP,
    thumb_tip_index: int = THUMB_TIP,
    threshold: float = 0.05,
) -> tuple[float, bool]:
    """
    Normalized distance between the thumb tip and one fingertip.
    Returns (ratio, is_pinch) where ratio = dist / hand_size.
    """
    thumb_tip = landmarks[thumb_tip_index, :2]
    finger_tip = landmarks[finger_tip_index, :2]
    dist = float(np.linalg.norm(thumb_tip - finger_tip))
    scale = hand_scale(landmarks)
    ratio = dist / scale
    return ratio, ratio < threshold


class PinchStateMachine:
    """Debounced pinch open/closed with optional hold-to-click timing."""

    def __init__(
        self,
        activate_frames: int = 3,
        release_frames: int = 3,
        click_hold_seconds: float = 0.0,
    ) -> None:
        self.activate_frames = activate_frames
        self.release_frames = release_frames
        self.click_hold_seconds = max(0.0, float(click_hold_seconds))
        self._high = 0
        self._low = 0
        self._pinched = False
        self._held_seconds = 0.0
        self._click_fired = False

    def reset(self) -> None:
        self._high = 0
        self._low = 0
        self._pinched = False
        self._held_seconds = 0.0
        self._click_fired = False

    @property
    def held_seconds(self) -> float:
        return self._held_seconds

    def update(self, is_pinch_raw: bool, dt_seconds: float) -> tuple[bool, bool]:
        """
        Returns (pinched_stable, click_triggered).
        When click_hold_seconds is 0, the click fires on stable pinch activation.
        Otherwise it fires once after the stable pinch has been held long enough.
        """
        click_triggered = False
        if is_pinch_raw:
            self._high += 1
            self._low = 0
        else:
            self._low += 1
            self._high = 0

        if not self._pinched and self._high >= self.activate_frames:
            self._pinched = True
            self._held_seconds = 0.0
            self._click_fired = False
            if self.click_hold_seconds <= 0.0:
                self._click_fired = True
                click_triggered = True
        elif self._pinched and self._low >= self.release_frames:
            self._pinched = False
            self._held_seconds = 0.0
            self._click_fired = False

        if self._pinched and not self._click_fired and self.click_hold_seconds > 0.0:
            self._held_seconds += max(0.0, float(dt_seconds))
            if self._held_seconds >= self.click_hold_seconds:
                self._click_fired = True
                click_triggered = True

        return self._pinched, click_triggered
