from dataclasses import dataclass
from typing import Any, List, Optional

import cv2
import numpy as np
from mediapipe.tasks.python.core import base_options
from mediapipe.tasks.python.vision import HandLandmarker, HandLandmarkerOptions
from mediapipe.tasks.python.vision.core import image as image_lib
from mediapipe.tasks.python.vision.core import vision_task_running_mode

from handos.vision.model_asset import ensure_hand_landmarker_model

_RunningMode = vision_task_running_mode.VisionTaskRunningMode


@dataclass
class HandDetection:
    """One hand: 21 landmarks × (x, y, z) in normalized image space."""

    landmarks: np.ndarray  # shape (21, 3), float64
    handedness: str  # "Right" or "Left"
    handedness_score: float


class HandLandmarkDetector:
    """MediaPipe Tasks HandLandmarker (video mode)."""

    def __init__(
        self,
        max_num_hands: int = 1,
        min_hand_detection_confidence: float = 0.7,
        min_hand_presence_confidence: float = 0.6,
        min_tracking_confidence: float = 0.6,
    ) -> None:
        model_path = str(ensure_hand_landmarker_model())
        options = HandLandmarkerOptions(
            base_options=base_options.BaseOptions(model_asset_path=model_path),
            running_mode=_RunningMode.VIDEO,
            num_hands=max_num_hands,
            min_hand_detection_confidence=min_hand_detection_confidence,
            min_hand_presence_confidence=min_hand_presence_confidence,
            min_tracking_confidence=min_tracking_confidence,
        )
        self._landmarker = HandLandmarker.create_from_options(options)
        self._last_ts_ms = 0

    def close(self) -> None:
        self._landmarker.close()

    def _next_timestamp_ms(self) -> int:
        # Monotonic ms for VIDEO mode (required by MediaPipe).
        self._last_ts_ms += 33
        return self._last_ts_ms

    def process_bgr(self, frame_bgr: Any) -> Optional[List[HandDetection]]:
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        rgb = np.ascontiguousarray(rgb)
        mp_image = image_lib.Image(image_lib.ImageFormat.SRGB, rgb)
        result = self._landmarker.detect_for_video(mp_image, self._next_timestamp_ms())

        if not result.hand_landmarks:
            return None

        out: List[HandDetection] = []
        for hi, lm_list in enumerate(result.hand_landmarks):
            pts = np.zeros((21, 3), dtype=np.float64)
            for i, lm in enumerate(lm_list):
                pts[i, 0] = float(lm.x)
                pts[i, 1] = float(lm.y)
                pts[i, 2] = float(lm.z)

            label = "Unknown"
            score = 0.0
            if hi < len(result.handedness) and result.handedness[hi]:
                top = result.handedness[hi][0]
                label = str(top.category_name or "Unknown")
                score = float(top.score or 0.0)

            out.append(HandDetection(landmarks=pts, handedness=label, handedness_score=score))
        return out
