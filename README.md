# Conductor Demo

Webcam-based conducting demo with split-hand gesture control and a single demo-song playback backend.

Current scope:
- modular package layout for `vision`, `motion`, `music`, `ui`, `config`, and `app`
- OpenCV webcam capture
- MediaPipe hand tracking
- stable left/right wrist tracking with short hold recovery
- separate motion buffers for right-hand tempo and left-hand dynamics
- right-hand tempo estimation from recent motion energy
- left-hand dynamics estimation from recent motion span
- one-song WAV playback backend with play/pause/resume/reset, tempo, and volume control
- lightweight debug overlay
- simple calibration hook and keyboard fallback controls

Playback backend choice:
- the project now uses a small `wave + sounddevice` backend instead of VLC
- reason: it avoids an external VLC install and keeps rate/volume control inside Python for a safer classroom demo
- current limitation: the demo track should be a PCM WAV file

## Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

The default demo song is:

```text
assets/audio/demo_song.wav
```

You can replace it with your own PCM WAV track or override it on launch:

```bash
python main.py --demo-track path/to/your_song.wav
```

On the first run, the app will download the MediaPipe hand model automatically if `assets/models/hand_landmarker.task` is missing.

Quick smoke test without opening the webcam:

```bash
python main.py --self-test --verbose
```

Run the webcam loop for a short check:

```bash
python main.py --max-frames 300
```

Controls:
- `S`: start the song from the beginning
- `P`: pause playback
- `G`: resume playback
- `Space`: safe pause / resume toggle
- `R`: safe reset and playback recovery while keeping the last completed calibration
- `C`: run a short split-hand calibration for right-hand tempo and left-hand dynamics
- `[` / `]`: decrease / increase tempo trim on top of gesture tempo
- `Esc`: quit

Playback safety:
- manual keyboard fallback is the primary transport control for the demo
- the on-screen playback panel always shows `STOPPED`, `PLAYING`, `PAUSED`, `ENDED`, or `AUDIO ERROR`
- `R` is the recovery key: it resets transport state, rebuilds audio if playback errors out, and keeps the last completed calibration
- if gesture cue controls are added later, they should remain secondary to these manual keys

Calibration:
- press `C`, show both hands, hold a relaxed neutral pose for about 1 second, then conduct naturally for about 2 seconds
- calibration estimates left-hand dynamics span plus right-hand tempo motion gate
- you can recalibrate at any time during the demo; the previous calibration stays active until the new one finishes

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

The current entrypoint opens the webcam, tracks both hands, and assigns stable roles:
- right hand: tempo -> playback rate
- left hand: dynamics -> playback volume

Gesture tempo remains recoverable with manual `[` / `]` tempo trim, and transport remains on keyboard fallback controls for demo safety.
