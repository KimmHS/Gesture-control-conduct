# 2026-06-17 Report 83 - Selected TCN Live Bundle

## Scope

Export the current TCN handmark live candidate into a selected bundle containing:

- model checkpoint
- live manifest
- model structure / parameter description
- linked score, gate, readiness, and benchmark evidence

This makes the current live-facing model easier to copy into a runtime integration.

## Code Changes

```text
lib/right_conducting/tcn_export.py
tools/export_tcn_live_bundle.py
tools/run_right_conducting_goal.py
tests/test_tcn_live.py
tests/test_goal_command_cli.py
```

New goal runner step:

```text
export-tcn-selected
```

## Selected Bundle

```text
outputs/right_conducting/selected_tcn_handmark_live45f/
  tcn_conducting_head.pt
  tcn_conducting_live_manifest.json
  tcn_conducting_live_structure.md
  selected_stream_outputs.jsonl
  selected_stream_summary.json
  selected_stream_benchmark.json
  selected_stream_benchmark.md
  tcn_goal_runner_export_chain.json
  tcn_goal_runner_export_chain.md
```

## Model Parameters

```json
{
  "model_type": "causal_tcn_right_arm_pose",
  "input_shape": ["B", 45, 17, 3],
  "input_tensor_shape": ["B", 9, 45],
  "window_frames": 45,
  "stride_frames": 3,
  "fps": 15.0,
  "bpm_bins": [60, 80, 100, 120],
  "right_arm_indices": [14, 15, 16],
  "architecture": {
    "class": "ConductingTCN",
    "input_channels": 9,
    "hidden_channels": 64,
    "levels": 4,
    "kernel_size": 5,
    "dropout": 0.1,
    "tempo_classes": 4,
    "gain_classes": 2,
    "outputs": ["tempo_logits", "gain_logits"]
  },
  "live_policy": {
    "switch_threshold": 0.58,
    "fast_switch_threshold": 0.78,
    "confirm_updates": 2
  }
}
```

## Repro Command

```bash
python tools/run_right_conducting_goal.py \
  --steps tcn-handmark-csv-stream,tcn-handmark-csv-set-score,tcn-handmark-csv-set-gate,tcn-handmark-csv-benchmark,tcn-handmark-stream-readiness,export-tcn-selected \
  --tcn-checkpoint outputs/right_conducting/tcn_quick_probe_20260617/45f/tcn_conducting_head.pt \
  --handmark-csv-stream-csv dataset/transitions/session_20260617_022415_bpm120to120_beat2_small.csv \
  --handmark-csv-set-root dataset/static_variants_80,dataset/transitions \
  --handmark-csv-set-stable-only \
  --device cuda:0 \
  --tcn-export-dir outputs/right_conducting/selected_tcn_handmark_live45f \
  --output-json outputs/right_conducting/selected_tcn_handmark_live45f/tcn_goal_runner_export_chain.json \
  --output-md outputs/right_conducting/selected_tcn_handmark_live45f/tcn_goal_runner_export_chain.md
```

## Selected Checkpoint Smoke

The exported checkpoint was reloaded from the selected bundle and run on raw handmark CSV.

| metric | value |
|---|---:|
| stream rows | 216 |
| invalid outputs | 0 |
| raw tempo switches | 4 |
| smoothed tempo switches | 4 |
| valid right arm frame ratio | 1.0000 |

Benchmark from the selected checkpoint:

| metric | value |
|---|---:|
| p90 update time ms | 2.2745 |
| update budget ms | 200.0000 |
| headroom ratio | 87.9320 |
| realtime pass | 1 |

## Evidence

```text
manifest: outputs/right_conducting/selected_tcn_handmark_live45f/tcn_conducting_live_manifest.json
structure: outputs/right_conducting/selected_tcn_handmark_live45f/tcn_conducting_live_structure.md
checkpoint: outputs/right_conducting/selected_tcn_handmark_live45f/tcn_conducting_head.pt
runner chain: outputs/right_conducting/selected_tcn_handmark_live45f/tcn_goal_runner_export_chain.json
selected stream summary: outputs/right_conducting/selected_tcn_handmark_live45f/selected_stream_summary.json
selected benchmark: outputs/right_conducting/selected_tcn_handmark_live45f/selected_stream_benchmark.json
```

## Verification

```text
python -m py_compile lib/right_conducting/tcn_export.py tools/export_tcn_live_bundle.py tools/run_right_conducting_goal.py tests/test_tcn_live.py tests/test_goal_command_cli.py
PYTHONPATH=. python -m unittest discover -s tests -p 'test_tcn_live.py' -v
PYTHONPATH=. python -m unittest discover -s tests -p 'test_goal_command_cli.py' -v
```

Result:

```text
test_tcn_live.py: 7 OK
test_goal_command_cli.py: 38 OK
```

## Decision

Use `outputs/right_conducting/selected_tcn_handmark_live45f` as the current live-facing TCN bundle.

Scope remains fixed-camera deployment-fit. Strict independent heldout is still incomplete and must be evaluated separately before claiming generalization.
