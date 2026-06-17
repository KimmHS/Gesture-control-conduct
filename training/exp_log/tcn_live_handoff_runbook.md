# TCN Live Handoff Runbook

## Selected Bundle

```text
bundle: outputs/right_conducting/selected_tcn_handmark_live45f
release manifest: outputs/right_conducting/selected_tcn_handmark_live45f/tcn_live_release_manifest.json
model manifest: outputs/right_conducting/selected_tcn_handmark_live45f/tcn_conducting_live_manifest.json
checkpoint: outputs/right_conducting/selected_tcn_handmark_live45f/tcn_conducting_head.pt
structure: outputs/right_conducting/selected_tcn_handmark_live45f/tcn_conducting_live_structure.md
```

## Live Stdin Command

Use this when a handmark producer writes CSV rows to stdout:

```bash
python your_handmark_producer.py | python tools/run_tcn_handmark_csv_stream.py \
  --manifest outputs/right_conducting/selected_tcn_handmark_live45f/tcn_conducting_live_manifest.json \
  --handmark-csv - \
  --output-jsonl - \
  --output-summary-json outputs/right_conducting/selected_tcn_handmark_live45f/live_stdin_summary.json \
  --device cuda:0 \
  --flush-each-output
```

Output rows are `right_conducting_live_output_v1` JSONL. The MIDI-ready fields are:

```text
midi.tempo_bpm
midi.velocity_scale
midi.cc11_expression
tempo.class_index
tempo.bpm
gain.class_index
gain.value
state.valid
```

## Required Input Columns

```text
right_shoulder_x,right_shoulder_y,right_shoulder_conf,
right_elbow_x,right_elbow_y,right_elbow_conf,
right_wrist_x,right_wrist_y,right_wrist_conf
```

Optional columns:

```text
shoulder_center_x,shoulder_center_y,shoulder_center_conf,
neck_x,neck_y,neck_conf,
left_shoulder_x,left_shoulder_y,left_shoulder_conf
```

## Current Evidence

```text
goal status: outputs/right_conducting/tcn_alltest_latest/tcn_goal_status_fulltest_latest.json
live_status: GO
strict_heldout_status: NO_GO
score gate: outputs/right_conducting/tcn_alltest_latest/stream_set_gate_fulltest_latest.json
readiness: outputs/right_conducting/tcn_alltest_latest/stream_readiness.json
current status: outputs/right_conducting/tcn_alltest_latest/current_status_fulltest_latest.json
release validation: outputs/right_conducting/selected_tcn_handmark_live45f/tcn_live_release_manifest_validation_fulltest_latest.json
release manifest: outputs/right_conducting/selected_tcn_handmark_live45f/tcn_live_release_manifest.json
```

Latest fixed-camera supplied-set metrics:

| metric | value |
|---|---:|
| discovered raw CSV files | 15 |
| scoreable processed sessions | 11 |
| sample_count at margin 3s | 1824 |
| tempo_acc | 1.0000 |
| gain_acc | 1.0000 |
| 80/100/120 recall | 1.0000 / 1.0000 / 1.0000 |
| false_switches_per_min | 0.0000 |
| missed_switch_count | 0 |
| benchmark p90 ms | 1.9984 |
| stream contract errors | 0 |
| stdin contract errors | 0 |

## Strict Completion

Current strict heldout status is `NO_GO` because these roots are absent:

```text
dataset/strict_heldout_static_v1
dataset/strict_heldout_transitions_v1
```

After those roots are recorded, run the final chain from:

```text
scripts/run_tcn_strict_post_arrival_goal.sh
docs/exp/goal_reports/2026-06-17_101_strict_post_arrival_script.md
docs/exp/goal_reports/2026-06-17_117_full_test_release_and_status_rerun.md
docs/exp/goal_reports/2026-06-17_118_score_doc_and_runner_order_refresh.md
```

First verify the command with:

```bash
scripts/run_tcn_strict_post_arrival_goal.sh --dry-run
```

Then remove `--dry-run` after the strict roots exist. If `STRICT_STREAM_CSV` is unset, the script uses the default P0 filename when present, otherwise the first sorted `*.csv` directly under the strict transition root. You can still force a specific representative transition with `STRICT_STREAM_CSV=...`. The final chain starts with release validation and ends with `tcn-goal-status --fail-on-in-progress`.
