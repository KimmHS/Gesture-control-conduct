# 2026-06-17 Report 84 - Webcam Overlay Recovery and Full Tests

## Scope

The full unittest run exposed a missing live overlay script:

```text
tools/run_motionbert_webcam_overlay.py
```

This file is part of the live stream path, so it was restored instead of ignoring the failure.

## Code Change

```text
tools/run_motionbert_webcam_overlay.py
```

The script now provides:

- `build_overlay_lines()` with no camera or MediaPipe dependency
- CLI help for live webcam overlay usage
- lazy runtime imports for `cv2`, `mediapipe`, and `torch`
- webcam frame -> MediaPipe Pose -> H36M17 frame -> `OnlinePoseFrameStreamer`
- live overlay text drawing
- optional JSONL output
- `q` quit and `r` smoother reset controls

## Runtime Command

```bash
python tools/run_motionbert_webcam_overlay.py \
  --manifest outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/motionbert_conducting_live_manifest.json \
  --device cuda:0 \
  --camera-index 0 \
  --output-jsonl outputs/right_conducting/webcam_overlay_outputs.jsonl
```

This command requires:

```text
mediapipe
opencv-python
```

## Verification

Focused:

```text
python -m py_compile tools/run_motionbert_webcam_overlay.py
PYTHONPATH=. python -m unittest discover -s tests -p 'test_motionbert_webcam_overlay.py' -v
PYTHONPATH=. python -m unittest discover -s tests -p 'test_motionbert_mediapipe_pose.py' -v
```

Result:

```text
test_motionbert_webcam_overlay.py: 3 OK
test_motionbert_mediapipe_pose.py: 3 OK
```

Full suite:

```text
PYTHONPATH=. python -m unittest discover tests -v
```

Result:

```text
247 tests OK
```

## Decision

The selected TCN bundle remains the current live-facing model path. The restored webcam overlay gives a direct visual demo route for the existing MotionBERT pose-stream runtime; TCN raw handmark CSV/stdin remains the strongest scored live classifier path.
