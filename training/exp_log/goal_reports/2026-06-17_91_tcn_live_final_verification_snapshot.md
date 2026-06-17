# Report 91 — TCN Live Final Verification Snapshot

## Purpose

Freeze the current live-facing state after the full test run. This report separates what is deployment-fit for the fixed-camera supplied handmark data from what is still not proven as strict independent heldout generalization.

## Selected Runtime

```text
bundle: outputs/right_conducting/selected_tcn_handmark_live45f
manifest: outputs/right_conducting/selected_tcn_handmark_live45f/tcn_conducting_live_manifest.json
checkpoint: outputs/right_conducting/selected_tcn_handmark_live45f/tcn_conducting_head.pt
structure: outputs/right_conducting/selected_tcn_handmark_live45f/tcn_conducting_live_structure.md
model_type: causal_tcn_right_arm_pose
input: [B, 45, 17, 3] -> [B, 9, 45]
fps: 15
window: 45 frames, about 3.0s
stride: 3 frames, about 0.2s
bpm_bins: [60, 80, 100, 120]
right_arm_indices: [14, 15, 16]
```

## Fixed-Camera Supplied-Set Score

Artifact:

```text
outputs/right_conducting/selected_tcn_handmark_live45f/alltest_2beat3beat_stream_set_score.json
outputs/right_conducting/selected_tcn_handmark_live45f/alltest_2beat3beat_stream_set_gate.json
```

Scope:

```text
dataset/static_variants_80
dataset/transitions
beat4 CSV files excluded
stable_only: true
transition_margin_seconds: 3.0
csv_count: 11
eval_session_count: 11
```

| metric | value |
|---|---:|
| sample_count | 1824 |
| mixed_bpm_excluded_count | 204 |
| transition_margin_excluded_count | 423 |
| smoothed tempo_acc | 1.0000 |
| smoothed gain_acc | 1.0000 |
| 80 BPM recall / support | 1.0000 / 1152 |
| 100 BPM recall / support | 1.0000 / 191 |
| 120 BPM recall / support | 1.0000 / 481 |
| small gain recall / support | 1.0000 / 850 |
| large gain recall / support | 1.0000 / 974 |
| bpm_mae_window | 0.0000 |
| false_switches_per_min | 0.0000 |
| switch_delay_p90_s | 0.0000 |
| missed_switch_count | 0 |

Gate result:

```text
status: GO
selected_margin_seconds: 3.0
true_switch_count: 14
pred_switch_count: 14
false_switch_count: 0
```

## Live Output Contract

Artifacts:

```text
outputs/right_conducting/selected_tcn_handmark_live45f/alltest_2beat3beat_stream_outputs.jsonl
outputs/right_conducting/selected_tcn_handmark_live45f/alltest_2beat3beat_stream_outputs_contract.json
outputs/right_conducting/selected_tcn_handmark_live45f/stdin_smoke_outputs.jsonl
outputs/right_conducting/selected_tcn_handmark_live45f/stdin_smoke_outputs_contract.json
outputs/right_conducting/selected_tcn_handmark_live45f/alltest_2beat3beat_stream_readiness_with_output_contract.json
```

| check | status | rows | errors |
|---|---:|---:|---:|
| alltest stream JSONL contract | GO | 216 | 0 |
| stdin smoke JSONL contract | GO | 3 | 0 |
| readiness v3 with output contract | GO | 216 stream / 3 stdin | 0 |

The readiness artifact uses schema `right_conducting_tcn_handmark_stream_readiness_v3` and validates both the scored stream output JSONL and the stdin live-smoke JSONL against the live output contract.

## Runtime Benchmark

Artifact:

```text
outputs/right_conducting/selected_tcn_handmark_live45f/alltest_2beat3beat_stream_benchmark.json
```

| metric | value |
|---|---:|
| device | cuda:0 |
| output_count | 216 |
| per-output mean ms | 1.6180 |
| per-output p90 ms | 1.6854 |
| per-output p95 ms | 1.7501 |
| per-output max ms | 2.0366 |
| realtime headroom ratio | 118.6673 |

The runtime is comfortably below the 0.2s update interval from the 3-frame stride at 15 FPS.

## Verification

```bash
PYTHONPATH=. python -m unittest discover tests -v
```

Result:

```text
Ran 252 tests in 56.417s
OK
```

Focused checks already covered:

```text
test_live_output_contract.py: 8 OK
test_tcn_live.py: 10 OK
test_goal_command_cli.py: 38 OK
```

## Strict Heldout Status

Artifact:

```text
outputs/right_conducting/selected_tcn_handmark_live45f/alltest_strict_heldout_preflight.json
```

Current strict status:

```text
strict_heldout_preflight: NO_GO
independence_status: NO_GO
scope_status: NO_GO
p0_complete: false
missing roots:
  dataset/strict_heldout_static_v1
  dataset/strict_heldout_transitions_v1
```

Reason: the strict heldout roots are not present, so the current fixed-camera supplied-set score must not be reported as strict independent generalization.

## Decision

Use the selected TCN bundle as the current live-facing fixed-camera handmark runtime:

```text
outputs/right_conducting/selected_tcn_handmark_live45f/tcn_conducting_live_manifest.json
```

The current reportable claim is:

```text
GO for fixed-camera supplied 2/3-beat handmark replay and live JSONL contract.
NO_GO for strict independent heldout generalization until the strict heldout roots are recorded and the post-arrival chain passes.
```

