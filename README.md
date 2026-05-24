# Conductor Demo

Webcam-based conducting demo with live hand tracking, motion-driven dynamics, and a single demo-song playback backend.

Current scope:
- modular package layout for `vision`, `motion`, `music`, `ui`, `config`, and `app`
- OpenCV webcam capture
- MediaPipe hand tracking
- stable main-hand wrist extraction for trajectory-based control
- smoothing, confidence handling, and rolling motion buffer
- motion-driven dynamics estimation
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

MediaPipe currently needs a supported Python build for the webcam runtime. On macOS, use Python 3.11 or 3.12 for the full camera demo. Python 3.13 can install the non-MediaPipe dependencies and run the pure unit tests, but the webcam tracker will report that MediaPipe is unavailable.

The default demo song is:

```text
assets/audio/demo_song.wav
```

You can replace it with your own PCM WAV track or override it on launch:

```bash
python main.py --demo-track path/to/your_song.wav
```

## MIDI + Two-Hand Landmark Control

The demo now includes a two-hand section mixer:

- left index fingertip selects `STRINGS`, `WOODWINDS`, `BRASS`, `PERCUSSION`, or `TUTTI` on the overlay
- right wrist motion controls expression for the selected section
- right downward strokes trigger section cue commands
- optional MIDI output sends CC11 Expression to a macOS MIDI port

Inspect the included MIDI file:

```bash
PYTHONPATH=src python -m conductor_demo.music.midi_inspect assets/audio/Symphony7_2.mid
```

Run visual mapping only:

```bash
python main.py
```

Run with macOS IAC MIDI output:

```bash
python main.py --midi-out "IAC Driver Bus 1"
```

On macOS, enable the IAC Driver in **Audio MIDI Setup** first, then route that bus into a DAW or software instrument. `Symphony7_2.mid` currently maps woodwinds to channels `0-5`, percussion/timpani to channel `6`, and strings to channels `7, 8, 10, 11, 12`; there is no brass channel in the current MIDI file, so the `BRASS` gesture zone is visual/scoring-only until a brass track is added or remapped.

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
- `C`: run a short calibration for neutral pose and comfortable motion range
- `[` / `]`: decrease / increase playback tempo
- `Esc`: quit

Playback safety:
- manual keyboard fallback is the primary transport control for the demo
- the on-screen playback panel always shows `STOPPED`, `PLAYING`, `PAUSED`, `ENDED`, or `AUDIO ERROR`
- `R` is the recovery key: it resets transport state, rebuilds audio if playback errors out, and keeps the last completed calibration
- if gesture cue controls are added later, they should remain secondary to these manual keys

Calibration:
- press `C`, hold your hand in a relaxed neutral pose for about 1 second, then conduct naturally for about 2 seconds
- calibration estimates your baseline wrist position, comfortable motion span, dynamics range, and tempo motion gate
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

The current entrypoint opens the webcam, tracks the most stable conducting hand, stores recent wrist positions, and renders a debug overlay.
Dynamics currently come from recent wrist-motion span and are mapped to playback volume.
Tempo control is wired to playback rate and can already be tested with the keyboard fallback controls.
