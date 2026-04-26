import queue
import threading
from typing import Any

import cv2

from handos.data import VisionPacket
from handos.vision.detector import HandLandmarkDetector


class VisionThread(threading.Thread):
    """Runs MediaPipe on frames from frame_queue; emits VisionPacket to out_queue."""

    def __init__(
        self,
        frame_queue: "queue.Queue[Any]",
        out_queue: "queue.Queue[VisionPacket]",
        include_frame_copy: bool,
        name: str = "HandOS-Vision",
    ) -> None:
        super().__init__(name=name, daemon=True)
        self._frame_queue = frame_queue
        self._out_queue = out_queue
        self._include_frame_copy = include_frame_copy
        self._stop = threading.Event()
        self._detector = HandLandmarkDetector()

    def stop(self) -> None:
        self._stop.set()

    def run(self) -> None:
        while not self._stop.is_set():
            try:
                frame = self._frame_queue.get(timeout=0.2)
            except queue.Empty:
                continue

            detections = self._detector.process_bgr(frame)
            frame_copy = frame.copy() if self._include_frame_copy else None

            if not detections:
                pkt = VisionPacket(
                    frame_bgr=frame_copy,
                    landmarks=None,
                    handedness="",
                    handedness_score=0.0,
                )
            else:
                primary = detections[0]
                pkt = VisionPacket(
                    frame_bgr=frame_copy,
                    landmarks=primary.landmarks,
                    handedness=primary.handedness,
                    handedness_score=primary.handedness_score,
                )

            if self._out_queue.full():
                try:
                    self._out_queue.get_nowait()
                except queue.Empty:
                    pass
            try:
                self._out_queue.put_nowait(pkt)
            except queue.Full:
                pass

        self._detector.close()
