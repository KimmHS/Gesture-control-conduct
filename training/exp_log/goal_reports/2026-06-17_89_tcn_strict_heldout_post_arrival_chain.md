# 2026-06-17 Report 89 - TCN Strict Heldout Post-Arrival Chain

## Scope

Fix the exact command chain to run after independent strict heldout data is recorded.

Current status is intentionally unchanged:

```text
fixed-camera live readiness with stdin: GO
strict independent heldout: NO_GO
reason: dataset/strict_heldout_static_v1 and dataset/strict_heldout_transitions_v1 are not present, P0 coverage 0/8
```

This report makes the next strict evaluation reproducible rather than manually assembled.

## Required Heldout Roots

```text
dataset/strict_heldout_static_v1
dataset/strict_heldout_transitions_v1
```

Required original artifacts per session:

```text
meta.json
labels_frame.jsonl
labels_window.jsonl
pose_right_h36m_masked.npy
right_rule_features.npy
```

Current P0 checklist:

```text
outputs/right_conducting/selected_tcn_handmark_live45f/alltest_strict_heldout_missing_checklist_preflight.md
```

## Dry-Run Artifact

Artifacts:

```text
outputs/right_conducting/selected_tcn_handmark_live45f/strict_v1_tcn_post_arrival_goal_dryrun.json
outputs/right_conducting/selected_tcn_handmark_live45f/strict_v1_tcn_post_arrival_goal_dryrun.md
```

The dry-run command includes:

```text
heldout-independence
strict-heldout-scope
strict-heldout-missing-checklist
strict-heldout-preflight --fail-on-no-go
tcn-handmark-csv-stream
tcn-handmark-csv-set-score
tcn-handmark-csv-set-gate
tcn-handmark-csv-benchmark
tcn-handmark-stream-readiness with stdin summary
```

The preflight step uses `--fail-on-no-go`, so if independence or P0 scope is not valid, the chain stops before reporting model scores.

## Post-Arrival Command

After the heldout roots exist, run:

```bash
python tools/run_right_conducting_goal.py \
  --steps heldout-independence,strict-heldout-scope,strict-heldout-missing-checklist,strict-heldout-preflight,tcn-handmark-csv-stream,tcn-handmark-csv-set-score,tcn-handmark-csv-set-gate,tcn-handmark-csv-benchmark,tcn-handmark-stream-readiness \
  --heldout-train-manifests outputs/right_conducting/recordings_staged_static80_transitions_manifest.json \
  --heldout-eval-roots dataset/strict_heldout_static_v1,dataset/strict_heldout_transitions_v1 \
  --heldout-target-static-root dataset/strict_heldout_static_v1 \
  --heldout-target-transition-root dataset/strict_heldout_transitions_v1 \
  --heldout-preflight-fail-on-no-go \
  --tcn-manifest outputs/right_conducting/selected_tcn_handmark_live45f/tcn_conducting_live_manifest.json \
  --handmark-csv-set-root dataset/strict_heldout_static_v1,dataset/strict_heldout_transitions_v1 \
  --handmark-csv-set-stable-only \
  --handmark-csv-stream-csv dataset/strict_heldout_transitions_v1/P0_transition_120_to_80_to_120_beat2_small.csv \
  --device cuda:0 \
  --heldout-independence-output-json outputs/right_conducting/selected_tcn_handmark_live45f/strict_v1_tcn_heldout_independence.json \
  --heldout-scope-output-json outputs/right_conducting/selected_tcn_handmark_live45f/strict_v1_tcn_heldout_scope.json \
  --heldout-missing-output-json outputs/right_conducting/selected_tcn_handmark_live45f/strict_v1_tcn_missing_checklist.json \
  --heldout-preflight-output-json outputs/right_conducting/selected_tcn_handmark_live45f/strict_v1_tcn_preflight.json \
  --tcn-handmark-csv-stream-output-jsonl outputs/right_conducting/selected_tcn_handmark_live45f/strict_v1_tcn_stream_outputs.jsonl \
  --tcn-handmark-csv-stream-summary-json outputs/right_conducting/selected_tcn_handmark_live45f/strict_v1_tcn_stream_summary.json \
  --tcn-handmark-csv-set-score-json outputs/right_conducting/selected_tcn_handmark_live45f/strict_v1_tcn_stream_set_score.json \
  --tcn-handmark-csv-set-gate-json outputs/right_conducting/selected_tcn_handmark_live45f/strict_v1_tcn_stream_set_gate.json \
  --tcn-handmark-csv-benchmark-json outputs/right_conducting/selected_tcn_handmark_live45f/strict_v1_tcn_stream_benchmark.json \
  --tcn-handmark-stream-readiness-stdin-summary-json outputs/right_conducting/selected_tcn_handmark_live45f/stdin_smoke_summary.json \
  --tcn-handmark-stream-readiness-json outputs/right_conducting/selected_tcn_handmark_live45f/strict_v1_tcn_readiness_with_stdin.json \
  --output-json outputs/right_conducting/selected_tcn_handmark_live45f/strict_v1_tcn_post_arrival_goal_run.json \
  --output-md outputs/right_conducting/selected_tcn_handmark_live45f/strict_v1_tcn_post_arrival_goal_run.md
```

Replace the `--handmark-csv-stream-csv` value with any real strict transition CSV if the exact placeholder filename differs.

## Pass Line

Strict TCN pass requires all of:

| gate | required |
|---|---|
| heldout independence | GO |
| strict P0 scope | P0 8/8 present |
| strict preflight | GO |
| score gate margin | 3.0s |
| sample count | >= 1000 |
| eval sessions | >= 10 |
| tempo_acc | >= 0.98 |
| gain_acc | >= 0.95 |
| 80 recall | >= 0.90 |
| 100 recall | >= 0.90 |
| 120 recall | >= 0.90 |
| false switches/min | <= 0.50 |
| missed switches | 0 |
| benchmark | p90 < 200ms update interval |
| stdin smoke | schema pass, rows >= 1, invalid 0 |

## Verification

```text
python tools/run_right_conducting_goal.py --dry-run ...
```

Result:

```text
dry-run artifact written
strict stream summary path is strict_v1_tcn_stream_summary.json
readiness gate consumes strict_v1_tcn_stream_summary.json plus stdin_smoke_summary.json
```

## Decision

The post-arrival strict heldout path is now fixed. Current selected TCN remains live-ready for the fixed-camera supplied set, but the goal remains incomplete until strict heldout data is recorded and this chain passes.
