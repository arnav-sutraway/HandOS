from typing import Optional, Tuple


class DeadZone:
    """Suppress micro-movements in pixel space before sending to the OS."""

    def __init__(self, threshold_px: float = 5.0) -> None:
        self.threshold_px = threshold_px
        self._last_sent: Optional[Tuple[float, float]] = None

    def reset(self) -> None:
        self._last_sent = None

    def apply(self, x: float, y: float) -> Optional[Tuple[float, float]]:
        """
        Returns None if the movement is below the dead zone (caller should not move cursor).
        Otherwise returns the clamped target position and updates internal state.
        """
        if self._last_sent is None:
            self._last_sent = (x, y)
            return (x, y)

        dx = x - self._last_sent[0]
        dy = y - self._last_sent[1]
        if abs(dx) < self.threshold_px and abs(dy) < self.threshold_px:
            return None

        self._last_sent = (x, y)
        return (x, y)
