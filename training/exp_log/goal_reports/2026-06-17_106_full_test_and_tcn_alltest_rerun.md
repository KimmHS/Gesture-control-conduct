# Report 106 - Full Test and TCN Supplied-Set Rerun

## Purpose

User request: "전체다 돌려서 테스트해".

This report records the latest verification pass for the current selected TCN handmark live bundle.

## Scope

```text
selected bundle: outputs/right_conducting/selected_tcn_handmark_live45f
model: causal_tcn_right_arm_pose
checkpoint: outputs/right_conducting/selected_tcn_handmark_live45f/tcn_conducting_head.pt
manifest: outputs/right_conducting/selected_tcn_handmark_live45f/tcn_conducting_live_manifest.json
fps: 15
window_frames: 45
stride_frames: 3
tempo bins: 60 / 80 / 100 / 120
gain bins: small / large
```

The supplied-set rerun used original handmark CSV artifacts only:

```text
dataset/static_variants_80
dataset/transitions
```

4-beat CSV files were excluded. The effective scoring set is 11 CSV sessions:

```text
4 static 80 BPM takes
7 transition takes
```

This is deployment-fit evidence for the current fixed-camera supplied set. It is not strict independent heldout evidence because the strict heldout roots are still missing.

## Commands Run

Full unit/CLI regression suite:

```bash
PYTHONPATH=. python -m unittest discover tests -v
```

Selected TCN release validation:

```bash
python tools/check_tcn_live_release_manifest.py \
  --manifest outputs/right_conducting/selected_tcn_handmark_live45f/tcn_live_release_manifest.json \
  --output-json outputs/right_conducting/selected_tcn_handmark_live45f/tcn_live_release_manifest_validation_latest.json \
  --output-md outputs/right_conducting/selected_tcn_handmark_live45f/tcn_live_release_manifest_validation_latest.md \
  --fail-on-no-go
```

Latest supplied-set runtime rerun:

```bash
python tools/run_right_conducting_goal.py \
  --steps tcn-handmark-csv-stream,tcn-handmark-csv-set-score,tcn-handmark-csv-set-gate,tcn-handmark-csv-benchmark,tcn-handmark-stream-readiness \
  --tcn-manifest outputs/right_conducting/selected_tcn_handmark_live45f/tcn_conducting_live_manifest.json \
  --handmark-csv-stream-csv dataset/transitions/session_20260617_022415_bpm120to120_beat2_small.csv \
  --handmark-csv-set-root "$CSV_LIST_WITHOUT_BEAT4" \
  --handmark-csv-set-stable-only \
  --device cuda:0 \
  --tcn-handmark-csv-stream-output-jsonl outputs/right_conducting/tcn_alltest_latest/stream_outputs.jsonl \
  --tcn-handmark-csv-stream-summary-json outputs/right_conducting/tcn_alltest_latest/stream_summary.json \
  --tcn-handmark-csv-set-score-json outputs/right_conducting/tcn_alltest_latest/stream_set_score.json \
  --tcn-handmark-csv-set-score-md outputs/right_conducting/tcn_alltest_latest/stream_set_score.md \
  --tcn-handmark-csv-set-rows-jsonl outputs/right_conducting/tcn_alltest_latest/stream_set_rows.jsonl \
  --tcn-handmark-csv-set-gate-json outputs/right_conducting/tcn_alltest_latest/stream_set_gate.json \
  --tcn-handmark-csv-set-gate-md outputs/right_conducting/tcn_alltest_latest/stream_set_gate.md \
  --tcn-handmark-csv-benchmark-json outputs/right_conducting/tcn_alltest_latest/stream_benchmark.json \
  --tcn-handmark-csv-benchmark-md outputs/right_conducting/tcn_alltest_latest/stream_benchmark.md \
  --tcn-handmark-stream-readiness-json outputs/right_conducting/tcn_alltest_latest/stream_readiness.json \
  --tcn-handmark-stream-readiness-md outputs/right_conducting/tcn_alltest_latest/stream_readiness.md \
  --tcn-handmark-stream-readiness-stdin-summary-json outputs/right_conducting/selected_tcn_handmark_live45f/stdin_smoke_summary.json \
  --tcn-handmark-stream-readiness-stdin-output-jsonl outputs/right_conducting/selected_tcn_handmark_live45f/stdin_smoke_outputs.jsonl \
  --output-json outputs/right_conducting/tcn_alltest_latest/goal_runner_chain.json \
  --output-md outputs/right_conducting/tcn_alltest_latest/goal_runner_chain.md
```

Latest goal status summary:

```bash
python tools/summarize_tcn_right_conducting_goal_status.py \
  --manifest outputs/right_conducting/selected_tcn_handmark_live45f/tcn_conducting_live_manifest.json \
  --gate-json outputs/right_conducting/tcn_alltest_latest/stream_set_gate.json \
  --readiness-json outputs/right_conducting/tcn_alltest_latest/stream_readiness.json \
  --benchmark-json outputs/right_conducting/tcn_alltest_latest/stream_benchmark.json \
  --strict-preflight-json outputs/right_conducting/selected_tcn_handmark_live45f/report99_strict_heldout_preflight.json \
  --output-json outputs/right_conducting/tcn_alltest_latest/tcn_goal_status.json \
  --output-md outputs/right_conducting/tcn_alltest_latest/tcn_goal_status.md
```

Strict post-arrival chain check:

```bash
scripts/run_tcn_strict_post_arrival_goal.sh --dry-run
scripts/run_tcn_strict_post_arrival_goal.sh
```

The non-dry run exits with status 1 as expected because strict heldout data roots are absent.

## Test Result

```text
Ran 264 tests in 54.287s
OK
```

## TCN Supplied-Set Score

Artifacts:

```text
outputs/right_conducting/tcn_alltest_latest/stream_set_score.md
outputs/right_conducting/tcn_alltest_latest/stream_set_score.json
outputs/right_conducting/tcn_alltest_latest/stream_set_rows.jsonl
```

Margin sweep:

| margin_s | samples | mixed_excluded | margin_excluded | raw_tempo | smooth_tempo | smooth_gain | false/min | p90_s | missed | r80 | r100 | r120 | bpm_mae |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.0 | 2241 | 204 | 6 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | 0.0000 | 0 | 1.0000 | 1.0000 | 1.0000 | 0.0000 |
| 0.5 | 2172 | 204 | 75 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | 0.0000 | 0 | 1.0000 | 1.0000 | 1.0000 | 0.0000 |
| 1.0 | 2103 | 204 | 144 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | 0.0000 | 0 | 1.0000 | 1.0000 | 1.0000 | 0.0000 |
| 2.0 | 1964 | 204 | 283 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | 0.0000 | 0 | 1.0000 | 1.0000 | 1.0000 | 0.0000 |
| 3.0 | 1824 | 204 | 423 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | 0.0000 | 0 | 1.0000 | 1.0000 | 1.0000 | 0.0000 |

Selected gate row at 3s margin:

```text
status: GO
sample_count: 1824
eval_session_count: 11
tempo_acc: 1.0000
gain_acc: 1.0000
tempo_80_recall: 1.0000
tempo_100_recall: 1.0000
tempo_120_recall: 1.0000
false_switches_per_min: 0.0000
missed_switch_count: 0
bpm_mae_window: 0.0000
```

## Runtime Result

Artifacts:

```text
outputs/right_conducting/tcn_alltest_latest/stream_readiness.md
outputs/right_conducting/tcn_alltest_latest/stream_benchmark.md
outputs/right_conducting/tcn_alltest_latest/stream_outputs.jsonl
outputs/right_conducting/tcn_alltest_latest/stream_summary.json
```

Runtime summary:

```text
readiness: GO
stream_rows: 216
stream_invalid_count: 0
stdin_rows: 3
stdin_invalid_count: 0
stream_output_contract_status: GO
stream_output_contract_errors: 0
stdin_output_contract_status: GO
stdin_output_contract_errors: 0
benchmark_p90_ms: 1.9984
benchmark_headroom_ratio: 100.0821
update_budget_ms: 200.0000
```

## Release and Goal Status

Release manifest validation:

```text
status: GO
error_count: 0
artifact: outputs/right_conducting/selected_tcn_handmark_live45f/tcn_live_release_manifest_validation_latest.json
```

Goal status:

```text
artifact: outputs/right_conducting/tcn_alltest_latest/tcn_goal_status.json
status: IN_PROGRESS
live_status: GO
strict_heldout_status: NO_GO
```

Strict heldout preflight:

```text
status: NO_GO
independence_status: NO_GO
scope_status: NO_GO
P0 required / present / missing: 8 / 0 / 8
missing roots:
  dataset/strict_heldout_static_v1
  dataset/strict_heldout_transitions_v1
```

## Interpretation

Current live-facing model is TCN, not MotionBERT:

```text
model_type: causal_tcn_right_arm_pose
runtime entrypoint: tools/run_tcn_handmark_csv_stream.py --manifest
```

The current fixed-camera supplied set passes all live/runtime gates. The 80 BPM middle segments are classified correctly after transition margin removal, so the previous 80-tail recall collapse is fixed for this supplied-set scope.

This still does not close the full goal because strict independent heldout roots are missing. The final claim must wait until the strict post-arrival chain passes on:

```text
dataset/strict_heldout_static_v1
dataset/strict_heldout_transitions_v1
```

## Next Action

After strict heldout data arrives:

```bash
scripts/run_tcn_strict_post_arrival_goal.sh --dry-run
scripts/run_tcn_strict_post_arrival_goal.sh
```

Expected final pass line:

```text
release validation: GO
strict preflight: GO
TCN stream set gate: GO
TCN readiness: GO
goal status: COMPLETE
```
