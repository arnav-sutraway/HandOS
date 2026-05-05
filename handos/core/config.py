from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class EngineConfig:
    """Runtime configuration shared by CLI and future GUI surfaces."""

    camera: int = 0
    width: int = 640
    height: int = 480
    include_frame_copy: bool = True
    enable_mouse_control: bool = True
    dead_zone: float = 5.0
    pinch_threshold: float = 0.30
    right_pinch_threshold: float = 0.34
    pinch_activate_frames: int = 3
    pinch_release_frames: int = 3
    pinch_click_hold_seconds: float = 0.0
    right_click_hold_seconds: float = 0.35
    debug_pinch: bool = False
    kalman_dt: float = 1.0 / 30.0
    camera_timeout_seconds: float = 8.0
