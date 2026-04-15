# Conductor Demo Skeleton

Minimal project skeleton for a webcam-based conducting demo.

Current scope:
- modular package layout for `vision`, `motion`, `music`, `ui`, `config`, and `app`
- OpenCV webcam capture
- MediaPipe hand tracking
- stable main-hand wrist extraction for trajectory-based control
- smoothing, confidence handling, and rolling motion buffer
- lightweight debug overlay
- placeholder calibration flow and fallback controls

## Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

Quick smoke test without opening the webcam:

```bash
python main.py --self-test --verbose
```

Run the webcam loop for a short check:

```bash
python main.py --max-frames 300
```

Controls:
- `Space`: toggle playback placeholder
- `R`: reset tracking and calibration placeholders
- `C`: set calibration placeholder from the current hand scale
- `Esc`: quit

## Structure

```text
src/conductor_demo/
  app/
  config/
  motion/
  music/
  ui/
  vision/
```

The current entrypoint opens the webcam, tracks the most stable conducting hand, stores recent wrist positions, and renders a debug overlay.
Tempo, dynamics, and playback control logic still come next.
