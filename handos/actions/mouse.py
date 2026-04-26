from typing import Optional, Tuple

import pyautogui


class MouseController:
    """Cross-platform mouse injection (Phase 1: move + left click)."""

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

    def click_left(self) -> None:
        pyautogui.click(button="left", _pause=False)
