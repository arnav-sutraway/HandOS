"""Download/cache MediaPipe task models (not shipped inside the mediapipe wheel)."""

from __future__ import annotations

import os
import sys
import urllib.request
from pathlib import Path

# Official bundle (float16); path is stable per MediaPipe model registry.
_HAND_LANDMARKER_URL = (
    "https://storage.googleapis.com/mediapipe-models/"
    "hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
)


def hand_landmarker_cache_path() -> Path:
    if sys.platform == "win32":
        base = os.environ.get("LOCALAPPDATA") or str(Path.home() / "AppData" / "Local")
        return Path(base) / "handos" / "models"
    xdg = os.environ.get("XDG_CACHE_HOME")
    if xdg:
        return Path(xdg) / "handos" / "models"
    return Path.home() / ".cache" / "handos" / "models"


def ensure_hand_landmarker_model() -> Path:
    """
    Return path to hand_landmarker.task, downloading it once into a user cache dir.
    """
    dest_dir = hand_landmarker_cache_path()
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / "hand_landmarker.task"
    if dest.is_file() and dest.stat().st_size > 1_000_000:
        return dest

    print("HandOS: downloading hand_landmarker.task (one-time, ~15 MB)...", flush=True)
    tmp = dest.with_suffix(".tmp")
    req = urllib.request.Request(
        _HAND_LANDMARKER_URL,
        headers={"User-Agent": "HandOS/0.1 (https://github.com/local)"},
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = resp.read()
    tmp.write_bytes(data)
    tmp.replace(dest)
    return dest
