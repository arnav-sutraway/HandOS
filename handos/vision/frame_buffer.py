from collections import deque
from typing import Deque, List, Optional

import numpy as np


class FrameBuffer:
    """Rolling buffer of recent landmark arrays for temporal models (Phase 4+)."""

    def __init__(self, maxlen: int = 15) -> None:
        self._buf: Deque[np.ndarray] = deque(maxlen=maxlen)

    def push(self, landmarks: np.ndarray) -> None:
        self._buf.append(landmarks.copy())

    def clear(self) -> None:
        self._buf.clear()

    def as_sequence(self) -> Optional[List[np.ndarray]]:
        if len(self._buf) < self._buf.maxlen:
            return None
        return list(self._buf)
