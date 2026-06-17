# Report 110 - Selected TCN Model Card Refresh

## Purpose

The score and current-status docs now identify the live model as TCN, but `right_hand_conducting_model_card.md` still opened with older MotionBERT candidate text. This report refreshes the model card entry point so it states the actual current selected model first.

## Updated File

```text
docs/exp/right_hand_conducting_model_card.md
```

## Current Selected Model

```text
bundle_name: selected_tcn_handmark_live45f
manifest_model_name: tcn_right_conducting_live
model_type: causal_tcn_right_arm_pose
status: LIVE_READY_STRICT_HELDOUT_PENDING
live_status: GO
strict_heldout_status: NO_GO
```

Selected artifacts:

```text
bundle: outputs/right_conducting/selected_tcn_handmark_live45f
manifest: outputs/right_conducting/selected_tcn_handmark_live45f/tcn_conducting_live_manifest.json
structure: outputs/right_conducting/selected_tcn_handmark_live45f/tcn_conducting_live_structure.md
checkpoint: outputs/right_conducting/selected_tcn_handmark_live45f/tcn_conducting_head.pt
release_manifest: outputs/right_conducting/selected_tcn_handmark_live45f/tcn_live_release_manifest.json
current_status_snapshot: outputs/right_conducting/tcn_alltest_latest/current_status_runner_snapshot.json
```

## Model Structure

```text
input: raw handmark CSV/stdin
pose window: [B, 45, 17, 3]
runtime tensor: [B, 9, 45]
right_arm_indices: [14, 15, 16]
fps: 15
stride_frames: 3
update_interval: about 0.2s
cold_start: about 3.0s
tempo_bins: 60 / 80 / 100 / 120
gain_classes: small / large
architecture: ConductingTCN
input_channels: 9
hidden_channels: 64
levels: 4
kernel_size: 5
dropout: 0.1
trainable_parameter_count: 147910
loss_terms: CE tempo + 0.5 CE gain
```

## Current Score

Latest supplied-set score:

```text
report: docs/exp/goal_reports/2026-06-17_106_full_test_and_tcn_alltest_rerun.md
score: outputs/right_conducting/tcn_alltest_latest/stream_set_score.json
gate: outputs/right_conducting/tcn_alltest_latest/stream_set_gate.json
readiness: outputs/right_conducting/tcn_alltest_latest/stream_readiness.json
benchmark: outputs/right_conducting/tcn_alltest_latest/stream_benchmark.json
```

Selected 3s transition-margin row:

```text
csv_count: 11
eval_session_count: 11
beat4: excluded
sample_count: 1824
tempo_acc: 1.0000
gain_acc: 1.0000
tempo_80_recall: 1.0000
tempo_100_recall: 1.0000
tempo_120_recall: 1.0000
bpm_mae_window: 0.0000
false_switches_per_min: 0.0000
missed_switch_count: 0
benchmark_p90_ms: 1.9984
stream_output_contract_errors: 0
stdin_output_contract_errors: 0
```

## Runtime Commands

File/CSV:

```bash
python tools/run_tcn_handmark_csv_stream.py \
  --manifest outputs/right_conducting/selected_tcn_handmark_live45f/tcn_conducting_live_manifest.json \
  --handmark-csv <input.csv> \
  --output-jsonl <live_outputs.jsonl> \
  --flush-each-output
```

Pipe/stdin:

```bash
python your_handmark_producer.py | python tools/run_tcn_handmark_csv_stream.py \
  --manifest outputs/right_conducting/selected_tcn_handmark_live45f/tcn_conducting_live_manifest.json \
  --handmark-csv - \
  --output-jsonl - \
  --flush-each-output
```

Current status:

```bash
python tools/run_right_conducting_goal.py --steps tcn-current-status
```

Strict post-arrival:

```bash
scripts/run_tcn_strict_post_arrival_goal.sh
```

## Limitation

The selected TCN is live-ready for the current fixed-camera supplied-set scope, but the full goal is not complete:

```text
strict heldout: NO_GO
missing roots:
  dataset/strict_heldout_static_v1
  dataset/strict_heldout_transitions_v1
P0 required / present / missing: 8 / 0 / 8
```

## Verification

The refresh is documentation-only. Values were checked against:

```text
outputs/right_conducting/selected_tcn_handmark_live45f/tcn_conducting_live_manifest.json
outputs/right_conducting/selected_tcn_handmark_live45f/tcn_live_release_manifest.json
outputs/right_conducting/tcn_alltest_latest/stream_set_gate.json
outputs/right_conducting/tcn_alltest_latest/current_status_runner_snapshot.json
outputs/right_conducting/selected_tcn_handmark_live45f/tcn_conducting_head.pt
```

Assertion result:

```text
selected_tcn_doc_and_artifact_assertions_ok
margin3_sample_count: 1824
tempo_acc: 1.0000
gain_acc: 1.0000
live_status: GO
strict_heldout_status: NO_GO
```

Full unittest:

```text
PYTHONPATH=. python -m unittest discover tests -v
Ran 270 tests in 58.982s
OK
```
