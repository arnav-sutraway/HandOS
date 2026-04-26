from dataclasses import dataclass
from typing import Optional

import numpy as np


@dataclass
class VisionPacket:
    """Output of the vision thread for one camera frame."""

    frame_bgr: Optional[np.ndarray]
    landmarks: Optional[np.ndarray]  # (21, 3) primary hand
    handedness: str
    handedness_score: float
