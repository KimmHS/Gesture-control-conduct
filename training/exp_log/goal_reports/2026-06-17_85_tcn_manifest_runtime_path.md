# 2026-06-17 Report 85 - TCN Manifest Runtime Path

## Scope

Make the selected TCN bundle runnable by manifest path, not only by direct checkpoint path.

This reduces integration friction: downstream runtime code can point to one manifest file and let the runtime resolve the checkpoint, model structure, policy, window size, FPS, and BPM bins.

## Code Changes

```text
lib/right_conducting/tcn_live.py
tools/run_tcn_handmark_csv_stream.py
tools/evaluate_tcn_handmark_csv_stream_set.py
tools/benchmark_tcn_handmark_csv_stream.py
tools/run_right_conducting_goal.py
tests/test_tcn_live.py
tests/test_goal_command_cli.py
```

## Runtime API

Python:

```python
from lib.right_conducting.tcn_live import TCNLivePredictor

predictor = TCNLivePredictor.from_manifest(
    "outputs/right_conducting/selected_tcn_handmark_live45f/tcn_conducting_live_manifest.json",
    device="cuda:0",
)
```

CLI:

```bash
python tools/run_tcn_handmark_csv_stream.py \
  --manifest outputs/right_conducting/selected_tcn_handmark_live45f/tcn_conducting_live_manifest.json \
  --handmark-csv dataset/transitions/session_20260617_022415_bpm120to120_beat2_small.csv \
  --device cuda:0
```

Goal runner:

```bash
python tools/run_right_conducting_goal.py \
  --steps tcn-handmark-csv-stream,tcn-handmark-csv-set-score,tcn-handmark-csv-set-gate,tcn-handmark-csv-benchmark,tcn-handmark-stream-readiness \
  --tcn-manifest outputs/right_conducting/selected_tcn_handmark_live45f/tcn_conducting_live_manifest.json \
  --handmark-csv-stream-csv dataset/transitions/session_20260617_022415_bpm120to120_beat2_small.csv \
  --handmark-csv-set-root dataset/static_variants_80,dataset/transitions \
  --handmark-csv-set-stable-only \
  --device cuda:0
```

## Manifest-Based Results

Artifacts:

```text
outputs/right_conducting/selected_tcn_handmark_live45f/manifest_stream_summary.json
outputs/right_conducting/selected_tcn_handmark_live45f/manifest_stream_set_score.json
outputs/right_conducting/selected_tcn_handmark_live45f/manifest_stream_set_gate.json
outputs/right_conducting/selected_tcn_handmark_live45f/manifest_stream_benchmark.json
outputs/right_conducting/selected_tcn_handmark_live45f/manifest_stream_readiness.json
outputs/right_conducting/selected_tcn_handmark_live45f/manifest_goal_runner_chain.json
```

Margin 3.0s, stable-only:

| metric | value |
|---|---:|
| sample_count | 1824 |
| smoothed tempo_acc | 1.0000 |
| smoothed gain_acc | 1.0000 |
| 80 BPM recall | 1.0000 |
| 100 BPM recall | 1.0000 |
| 120 BPM recall | 1.0000 |
| false_switches_per_min | 0.0000 |
| gate_status | GO |
| readiness_status | GO |

Runtime:

| metric | value |
|---|---:|
| stream rows | 216 |
| invalid outputs | 0 |
| benchmark p90 ms | 1.7361 |
| benchmark headroom ratio | 115.2018 |

## Verification

```text
python -m py_compile lib/right_conducting/tcn_live.py tools/run_tcn_handmark_csv_stream.py tools/benchmark_tcn_handmark_csv_stream.py tools/evaluate_tcn_handmark_csv_stream_set.py tools/run_right_conducting_goal.py tests/test_tcn_live.py tests/test_goal_command_cli.py
PYTHONPATH=. python -m unittest discover -s tests -p 'test_tcn_live.py' -v
PYTHONPATH=. python -m unittest discover -s tests -p 'test_goal_command_cli.py' -v
PYTHONPATH=. python -m unittest discover tests -v
```

Result:

```text
test_tcn_live.py: 8 OK
test_goal_command_cli.py: 38 OK
full unittest suite: 248 OK
```

## Decision

Use the manifest as the primary runtime entrypoint:

```text
outputs/right_conducting/selected_tcn_handmark_live45f/tcn_conducting_live_manifest.json
```

Keep direct checkpoint loading for debugging and backward compatibility.

Scope remains fixed-camera deployment-fit. Strict independent heldout is still incomplete.
