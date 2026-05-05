import ctypes
import sys
from typing import Optional, Tuple

import pyautogui


if sys.platform == "win32":
    INPUT_MOUSE = 0
    MOUSEEVENTF_LEFTDOWN = 0x0002
    MOUSEEVENTF_LEFTUP = 0x0004
    MOUSEEVENTF_RIGHTDOWN = 0x0008
    MOUSEEVENTF_RIGHTUP = 0x0010

    class MOUSEINPUT(ctypes.Structure):
        _fields_ = [
            ("dx", ctypes.c_long),
            ("dy", ctypes.c_long),
            ("mouseData", ctypes.c_ulong),
            ("dwFlags", ctypes.c_ulong),
            ("time", ctypes.c_ulong),
            ("dwExtraInfo", ctypes.c_void_p),
        ]

    class INPUT_UNION(ctypes.Union):
        _fields_ = [("mi", MOUSEINPUT)]

    class INPUT(ctypes.Structure):
        _anonymous_ = ("u",)
        _fields_ = [
            ("type", ctypes.c_ulong),
            ("u", INPUT_UNION),
        ]


class MouseController:
    """Cross-platform mouse injection for pointer movement and button clicks."""

    def __init__(self, screen_size: Optional[Tuple[int, int]] = None) -> None:
        if screen_size is None:
            self.screen_w, self.screen_h = pyautogui.size()
        else:
            self.screen_w, self.screen_h = screen_size
        pyautogui.FAILSAFE = False
        pyautogui.PAUSE = 0

    def move_to(self, x: float, y: float) -> None:
        xi = int(max(0, min(self.screen_w - 1, round(x))))
        yi = int(max(0, min(self.screen_h - 1, round(y))))
        pyautogui.moveTo(xi, yi, _pause=False)

    def click_left(self) -> bool:
        if sys.platform == "win32":
            return self._click_windows(MOUSEEVENTF_LEFTDOWN, MOUSEEVENTF_LEFTUP, button="left")
        pyautogui.click(button="left", _pause=False)
        return True

    def click_right(self) -> bool:
        if sys.platform == "win32":
            return self._click_windows(MOUSEEVENTF_RIGHTDOWN, MOUSEEVENTF_RIGHTUP, button="right")
        pyautogui.click(button="right", _pause=False)
        return True

    def _click_windows(self, down_flag: int, up_flag: int, *, button: str) -> bool:
        # Use SendInput on Windows so click injection stays consistent with the
        # existing low-latency left-click path. Fall back to pyautogui only if
        # the native call reports a partial send.
        inputs = (
            INPUT(type=INPUT_MOUSE, mi=MOUSEINPUT(dwFlags=down_flag)),
            INPUT(type=INPUT_MOUSE, mi=MOUSEINPUT(dwFlags=up_flag)),
        )
        sent = ctypes.windll.user32.SendInput(
            len(inputs),
            (INPUT * len(inputs))(*inputs),
            ctypes.sizeof(INPUT),
        )
        if sent != len(inputs):
            pyautogui.click(button=button, _pause=False)
            return False
        return True
