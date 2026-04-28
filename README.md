# HandOS

HandOS is a local, real-time hand gesture desktop control project.
The current implementation (`handos` package, Phase 1) uses a webcam and MediaPipe hand landmarks to:

- Move the mouse cursor using the index fingertip
- Trigger a left click using a pinch gesture (thumb + index), optionally after a sustained hold
- Smooth and stabilize motion with filtering and dead-zone suppression

All processing runs on-device. No cloud service is required.

## Features

- Real-time webcam capture and landmark detection
- Cursor control mapped from normalized hand coordinates to screen pixels
- Debounced pinch detection with optional hold-to-click confirmation to reduce accidental clicks
- Kalman-based cursor smoothing
- Pixel dead-zone filtering to suppress jitter
- Optional OpenCV preview window with hand overlay
- Cross-platform Python implementation (Windows-oriented defaults included)

## Quick Demo

![Demo GIF Moving](handos/assets/demo.gif "Demo Animation")
![Demo GIF Clicking](handos/assets/click_demo.gif "Click Demo Animation")

## Project Status

This repository is in active development with a Phase 1 foundation complete:

- Single-hand tracking (primary detected hand)
- Index-finger cursor movement
- Pinch-to-left-click

The codebase already includes scaffolding for later phases (for example, temporal buffers and EMA helpers), but these are not part of the current runtime behavior yet.

## Repository Layout

```text
DeviceGesture/
  handos/
    app.py                 # Main runtime loop and CLI
    __main__.py            # python -m handos entrypoint
    data.py                # VisionPacket data model
    actions/
      mouse.py             # OS mouse move/click wrapper (pyautogui)
    gestures/
      pinch.py             # Pinch metric + debounced state machine
    signal/
      kalman.py            # 2D constant-velocity Kalman filter
      dead_zone.py         # Micro-movement suppression
      ema.py               # Smoothing utility (future phases)
    vision/
      capture.py           # Camera capture thread
      worker.py            # Vision inference thread
      detector.py          # MediaPipe Tasks hand detector wrapper
      preprocessor.py      # Landmark/screen mapping + hand scale helpers
      model_asset.py       # One-time model download/cache logic
      frame_buffer.py      # Temporal buffer utility (future phases)
  requirements.txt
  pyproject.toml
```

## Requirements

- Python 3.10 or newer
- A webcam accessible by OpenCV
- OS permission to access camera
- OS permission for simulated mouse input (platform-dependent)

Python dependencies:

- `opencv-python`
- `mediapipe`
- `numpy`
- `pyautogui`

## Installation

From the project root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Alternative (editable package install):

```powershell
pip install -e .
```

## Running

Run as a module:

```powershell
python -m handos
```

Or run the app script directly:

```powershell
python .\handos\app.py
```

On first run, the app downloads the MediaPipe hand model (`hand_landmarker.task`) once and caches it locally.

### Quit Controls

- Press `q` in the preview window
- Press `Esc` in the preview window
- Send interrupt (`Ctrl+C`)

## Command-Line Options

The runtime exposes the following options:

- `--camera <int>`: OpenCV camera index (default `0`)
- `--no-preview`: Disable OpenCV preview window
- `--dead-zone <float>`: Pixel dead zone before cursor updates (default `5.0`)
- `--pinch-threshold <float>`: Pinch ratio threshold (default `0.30`)
- `--pinch-activate-frames <int>`: Consecutive pinch frames to activate click state (default `3`)
- `--pinch-release-frames <int>`: Consecutive open frames to release pinch state (default `3`)
- `--pinch-click-hold-seconds <float>`: Stable pinch hold time before one click fires (default `0.0`)
- `--debug-pinch`: Print pinch and click debug events to the terminal
- `--kalman-dt <float>`: Initial Kalman timestep in seconds (default `1/30`)
- `--width <int>`: Capture width (default `640`)
- `--height <int>`: Capture height (default `480`)

Example with custom tuning:

```powershell
python -m handos --camera 0 --width 1280 --height 720 --dead-zone 4 --pinch-threshold 0.30 --pinch-click-hold-seconds 1.0 --debug-pinch
```

## Runtime Architecture

The app is structured as a threaded pipeline:

1. `CameraThread` captures frames into a bounded queue.
2. `VisionThread` runs MediaPipe hand landmark inference and emits `VisionPacket`.
3. Main loop:
   - Maps index fingertip landmark to screen coordinates
   - Applies Kalman smoothing
   - Applies dead-zone suppression
   - Sends mouse movement through `pyautogui`
   - Computes pinch ratio and applies state-machine debouncing
   - Emits one left click once the pinch is confirmed, either immediately or after the configured hold time

This queue-based design keeps capture, inference, and control paths decoupled for better responsiveness.

## Performance and Tuning Notes

- Lower resolution (`640x480`) usually reduces latency and CPU load.
- If cursor feels shaky, increase `--dead-zone` slightly.
- If click misfires occur:
  - Increase `--pinch-activate-frames`
  - Decrease `--pinch-threshold` (requires tighter pinch)
  - Increase `--pinch-click-hold-seconds`
- If clicks feel delayed, decrease activation/release frame counts carefully.
- Use `--debug-pinch` to see the live pinch ratio and click events in the terminal.

## Model Caching

The hand landmark model is cached per user:

- Windows: `%LOCALAPPDATA%\handos\models\hand_landmarker.task`
- Linux/macOS: `$XDG_CACHE_HOME/handos/models` or `~/.cache/handos/models`

If the model file is missing or invalid, it is downloaded again.

## Troubleshooting

### Camera does not open

- Try a different index: `--camera 1`, `--camera 2`, etc.
- Close other applications using the webcam.
- Verify OS camera permissions for Python/terminal.

### App times out waiting for frames

- Confirm webcam is connected and not blocked by privacy settings.
- Lower capture resolution (`--width 640 --height 480`).
- Test camera separately with a minimal OpenCV script if needed.

### Cursor does not move or click

- Ensure hand is visible and well-lit.
- Check that your index fingertip is consistently in frame.
- On some platforms, grant accessibility/input automation permission for simulated mouse events.

### Preview window is not desired

- Run with `--no-preview`.

## Safety and Usage Guidance

Because this application controls the system pointer and can perform clicks:

- Start in a controlled environment
- Keep one hand near keyboard/mouse to stop the app quickly
- Use `Ctrl+C` to interrupt at any time
- Avoid running during critical desktop operations until tuned

## Development

Install in editable mode for local development:

```powershell
pip install -e .
```

Run directly:

```powershell
python -m handos --no-preview
```

The codebase currently focuses on runtime functionality and does not yet include a formal automated test suite.

## License

No license file is currently included in this repository. Add a license before external distribution.
