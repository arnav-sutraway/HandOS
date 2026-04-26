from typing import Optional, Tuple


class EMA2D:
    """Exponential moving average for 2D points (used in later phases with Kalman)."""

    def __init__(self, alpha: float = 0.35) -> None:
        self.alpha = min(max(alpha, 1e-6), 1.0)
        self._last: Optional[Tuple[float, float]] = None

    def reset(self) -> None:
        self._last = None

    def step(self, x: float, y: float) -> Tuple[float, float]:
        if self._last is None:
            self._last = (x, y)
            return x, y
        lx, ly = self._last
        a = self.alpha
        nx = a * x + (1.0 - a) * lx
        ny = a * y + (1.0 - a) * ly
        self._last = (nx, ny)
        return nx, ny
