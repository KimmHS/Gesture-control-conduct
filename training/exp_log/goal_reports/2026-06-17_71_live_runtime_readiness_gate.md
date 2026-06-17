# Live Runtime Readiness Gate

## Why

The selected ext bundle already has replay, benchmark, online pose stream, and live output artifacts. This report adds a single gate that checks whether those artifacts are actually present and internally consistent for the final stream path.

This is a live-pilot readiness gate, not a strict heldout generalization gate.

## Added

```text
lib/right_conducting/live_runtime_readiness.py
tools/check_motionbert_live_runtime_readiness.py
tools/run_right_conducting_goal.py step: live-runtime-readiness
```

The gate verifies:

```text
core model files
live output contract JSON/MD/sample schema
deployment live replay gate
full-backbone benchmark headroom
live output replay JSONL summaries
online frame-buffer pose stream evidence
window-scan vs online-buffer comparison
right-arm confidence degradation hold behavior
```

## Selected Bundle Result

Artifact:

```text
outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/live_runtime_readiness.json
outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/live_runtime_readiness.md
```

Summary:

| item | value |
|---|---:|
| status | GO |
| model | `motionbert_lite_right_conducting_live` |
| window_frames | 45 |
| stride_frames | 3 |
| fps | 15 |
| live output schema | `right_conducting_live_output_v1` |
| benchmark headroom | 17.1911 |
| live output replay cases | 2 |
| online pose stream cases | 2 |
| online comparison | PASS |
| pose quality degraded cases | 2 |

Runtime evidence:

| evidence | status | detail |
|---|---|---|
| contract | GO | schema `right_conducting_live_output_v1` |
| deployment gate | GO | deployment-fit live replay gate passes |
| benchmark | GO | p90 runtime fits 200ms update budget |
| live output replay | GO | static80 + transitions JSONL outputs exist |
| online pose stream | GO | online buffer matches window scan |
| pose quality gate | GO | degraded right-arm confidence is held |

## Command

```bash
python tools/run_right_conducting_goal.py \
  --steps live-runtime-readiness \
  --motionbert-export-dir outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext \
  --live-runtime-readiness-output-json outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/live_runtime_readiness.json \
  --live-runtime-readiness-output-md outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/live_runtime_readiness.md \
  --live-runtime-readiness-fail-on-no-go
```

## Live Stream Command Template

For a label-free pose sequence:

```bash
python tools/run_motionbert_pose_stream.py \
  --manifest outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/motionbert_conducting_live_manifest.json \
  --pose-npy PATH_TO_POSE_RIGHT_H36M_MASKED.npy \
  --online-buffer \
  --min-valid-right-arm-ratio 0.8 \
  --right-arm-confidence-threshold 0.0 \
  --output-jsonl outputs/right_conducting/live_stream_outputs.jsonl \
  --output-summary-json outputs/right_conducting/live_stream_summary.json
```

The output JSONL follows:

```text
outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/live_output_contract.json
```

Use `midi.tempo_bpm`, `midi.velocity_scale`, and `midi.cc11_expression` for downstream MIDI control.

## Strict Heldout Caveat

```text
live runtime readiness: GO
strict heldout preflight: NO_GO
strict heldout status: NO_GO
```

This means the bundle is runnable for the current fixed-camera live pilot, but final strict heldout robustness still requires the missing P0 heldout recordings.

## Verification

```bash
python -m py_compile lib/right_conducting/live_runtime_readiness.py tools/check_motionbert_live_runtime_readiness.py tools/run_right_conducting_goal.py
python -m unittest discover -s tests -p 'test_live_runtime_readiness.py' -v
python -m unittest discover -s tests -p 'test_goal_command_cli.py' -v
```

Result:

```text
test_live_runtime_readiness.py: 3 OK
test_goal_command_cli.py: 33 OK
```
