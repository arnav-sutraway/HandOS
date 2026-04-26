import queue
import sys
import threading
import time
from typing import Any, Optional

import cv2


class CameraThread(threading.Thread):
    """Captures frames from a webcam and pushes BGR frames into a bounded queue."""

    def __init__(
        self,
        frame_queue: "queue.Queue[Any]",
        device_index: int = 0,
        width: int = 640,
        height: int = 480,
        target_fps: float = 60.0,
        name: str = "HandOS-Camera",
    ) -> None:
        super().__init__(name=name, daemon=True)
        self._frame_queue = frame_queue
        self._device_index = device_index
        self._width = width
        self._height = height
        self._target_fps = target_fps
        self._stop = threading.Event()
        self._cap: Optional[cv2.VideoCapture] = None
        self.first_frame = threading.Event()

    def stop(self) -> None:
        self._stop.set()

    def run(self) -> None:
        if sys.platform == "win32":
            self._cap = cv2.VideoCapture(self._device_index, cv2.CAP_DSHOW)
            if not self._cap.isOpened():
                self._cap = cv2.VideoCapture(self._device_index)
        else:
            self._cap = cv2.VideoCapture(self._device_index)

        if not self._cap.isOpened():
            print(f"HandOS: could not open camera index {self._device_index}", file=sys.stderr)
            return

        self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, self._width)
        self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self._height)
        self._cap.set(cv2.CAP_PROP_FPS, self._target_fps)

        frame_interval = 1.0 / max(self._target_fps, 1.0)
        while not self._stop.is_set():
            t0 = time.perf_counter()
            ok, frame = self._cap.read()
            if not ok or frame is None:
                time.sleep(0.01)
                continue

            self.first_frame.set()

            if self._frame_queue.full():
                try:
                    self._frame_queue.get_nowait()
                except queue.Empty:
                    pass
            try:
                self._frame_queue.put_nowait(frame)
            except queue.Full:
                pass

            elapsed = time.perf_counter() - t0
            sleep_for = frame_interval - elapsed
            if sleep_for > 0:
                time.sleep(sleep_for)

        if self._cap is not None:
            self._cap.release()
            self._cap = None
