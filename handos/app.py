from __future__ import annotations

import argparse
import signal
import sys
import time
from typing import Optional

import cv2

from handos.core import EngineConfig, EngineEvent, GestureEngine
from handos.ui.overlay import render_preview


def _parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="HandOS Phase 1: index cursor + pinch click")
    p.add_argument("--camera", type=int, default=0, help="OpenCV camera index")
    p.add_argument("--no-preview", action="store_true", help="Disable OpenCV preview window")
    p.add_argument("--dead-zone", type=float, default=5.0, help="Dead zone in pixels")
    p.add_argument("--pinch-threshold", type=float, default=0.30, help="Pinch ratio threshold (smaller = tighter pinch)")
    p.add_argument("--pinch-activate-frames", type=int, default=3, help="Consecutive pinch frames to confirm")
    p.add_argument("--pinch-release-frames", type=int, default=3, help="Consecutive open frames to release pinch")
    p.add_argument(
        "--pinch-click-hold-seconds",
        type=float,
        default=0.0,
        help="Stable pinch hold time before clicking once (default 0.0 = immediate click)",
    )
    p.add_argument("--debug-pinch", action="store_true", help="Print pinch/click debug events to the terminal")
    p.add_argument("--kalman-dt", type=float, default=1.0 / 30.0, help="Initial Kalman dt seconds")
    p.add_argument("--width", type=int, default=640, help="Capture width")
    p.add_argument("--height", type=int, default=480, help="Capture height")
    return p.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> int:
    args = _parse_args(argv)
    stop = False

    def handle_sig(_sig, _frame) -> None:
        nonlocal stop
        stop = True

    signal.signal(signal.SIGINT, handle_sig)
    if sys.platform == "win32":
        signal.signal(signal.SIGBREAK, handle_sig)  # type: ignore[attr-defined]

    include_preview = not args.no_preview

    config = EngineConfig(
        camera=args.camera,
        width=args.width,
        height=args.height,
        include_frame_copy=include_preview,
        enable_mouse_control=True,
        dead_zone=args.dead_zone,
        pinch_threshold=args.pinch_threshold,
        pinch_activate_frames=args.pinch_activate_frames,
        pinch_release_frames=args.pinch_release_frames,
        pinch_click_hold_seconds=args.pinch_click_hold_seconds,
        debug_pinch=args.debug_pinch,
        kalman_dt=args.kalman_dt,
    )
    window = "HandOS (q or Esc to quit)"

    def on_event(event: EngineEvent) -> None:
        if event.kind == "pinch_debug":
            payload = event.payload
            print(
                (
                    f"[pinch] ratio={payload['ratio']:.3f} threshold={payload['threshold']:.3f} "
                    f"raw={payload['raw']} stable={payload['stable']}"
                ),
                flush=True,
            )
        elif event.kind == "click_triggered":
            payload = event.payload
            print(
                (
                    f"[click] triggered ratio={payload['ratio']:.3f} "
                    f"hold={payload['hold_seconds']:.2f}s status={payload['status']}"
                ),
                flush=True,
            )

    engine = GestureEngine(config, event_callback=on_event if args.debug_pinch else None)

    try:
        engine.start()
        while not stop:
            snapshot = engine.get_snapshot()
            if include_preview:
                vis = render_preview(snapshot, config)
                if vis is not None:
                    cv2.imshow(window, vis)
                key = cv2.waitKey(1) & 0xFF
                if key in (27, ord("q")):
                    break
            else:
                time.sleep(0.01)
        engine.stop()
        engine.wait_until_stopped()
    except RuntimeError as exc:
        print(f"HandOS: {exc}", file=sys.stderr)
        return 1
    finally:
        engine.stop()
        engine.wait_until_stopped()
        if include_preview:
            try:
                cv2.destroyAllWindows()
            except cv2.error:
                pass

    return 0
