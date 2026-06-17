# Report 93 - Strict Post-Arrival Final Chain

## Purpose

Regenerate the strict heldout post-arrival dry-run after the TCN completion audit was added. Report 89 fixed the strict scoring path. Reports 90-92 added output-contract readiness and `tcn-goal-status`. This report combines them into one final strict chain.

## Dry-Run Artifacts

```text
outputs/right_conducting/selected_tcn_handmark_live45f/strict_v1_tcn_final_post_arrival_goal_dryrun.json
outputs/right_conducting/selected_tcn_handmark_live45f/strict_v1_tcn_final_post_arrival_goal_dryrun.md
```

## Chain Order

```text
heldout-independence
strict-heldout-scope
strict-heldout-missing-checklist
strict-heldout-preflight --fail-on-no-go
tcn-handmark-csv-stream
tcn-handmark-csv-set-score
tcn-handmark-csv-set-gate
tcn-handmark-csv-benchmark
tcn-handmark-stream-readiness with stream/stdin JSONL output contract
tcn-goal-status --fail-on-in-progress
```

The final step writes:

```text
outputs/right_conducting/selected_tcn_handmark_live45f/strict_v1_tcn_final_goal_status.json
outputs/right_conducting/selected_tcn_handmark_live45f/strict_v1_tcn_final_goal_status.md
```

If strict data is missing, independence/scope/preflight fail before scoring. If scoring runs but any live or strict gate is weak, `tcn-goal-status --fail-on-in-progress` fails at the end.

## Final Post-Arrival Command

After these roots are recorded:

```text
dataset/strict_heldout_static_v1
dataset/strict_heldout_transitions_v1
```

run the same command without `--dry-run`:

```bash
python tools/run_right_conducting_goal.py \
  --steps heldout-independence,strict-heldout-scope,strict-heldout-missing-checklist,strict-heldout-preflight,tcn-handmark-csv-stream,tcn-handmark-csv-set-score,tcn-handmark-csv-set-gate,tcn-handmark-csv-benchmark,tcn-handmark-stream-readiness,tcn-goal-status \
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
  --heldout-independence-output-json outputs/right_conducting/selected_tcn_handmark_live45f/strict_v1_tcn_final_heldout_independence.json \
  --heldout-independence-output-md outputs/right_conducting/selected_tcn_handmark_live45f/strict_v1_tcn_final_heldout_independence.md \
  --heldout-scope-output-json outputs/right_conducting/selected_tcn_handmark_live45f/strict_v1_tcn_final_heldout_scope.json \
  --heldout-scope-output-md outputs/right_conducting/selected_tcn_handmark_live45f/strict_v1_tcn_final_heldout_scope.md \
  --heldout-missing-output-json outputs/right_conducting/selected_tcn_handmark_live45f/strict_v1_tcn_final_missing_checklist.json \
  --heldout-missing-output-md outputs/right_conducting/selected_tcn_handmark_live45f/strict_v1_tcn_final_missing_checklist.md \
  --heldout-preflight-output-json outputs/right_conducting/selected_tcn_handmark_live45f/strict_v1_tcn_final_preflight.json \
  --heldout-preflight-output-md outputs/right_conducting/selected_tcn_handmark_live45f/strict_v1_tcn_final_preflight.md \
  --tcn-handmark-csv-stream-output-jsonl outputs/right_conducting/selected_tcn_handmark_live45f/strict_v1_tcn_final_stream_outputs.jsonl \
  --tcn-handmark-csv-stream-summary-json outputs/right_conducting/selected_tcn_handmark_live45f/strict_v1_tcn_final_stream_summary.json \
  --tcn-handmark-csv-set-score-json outputs/right_conducting/selected_tcn_handmark_live45f/strict_v1_tcn_final_stream_set_score.json \
  --tcn-handmark-csv-set-score-md outputs/right_conducting/selected_tcn_handmark_live45f/strict_v1_tcn_final_stream_set_score.md \
  --tcn-handmark-csv-set-rows-jsonl outputs/right_conducting/selected_tcn_handmark_live45f/strict_v1_tcn_final_stream_set_rows.jsonl \
  --tcn-handmark-csv-set-gate-json outputs/right_conducting/selected_tcn_handmark_live45f/strict_v1_tcn_final_stream_set_gate.json \
  --tcn-handmark-csv-set-gate-md outputs/right_conducting/selected_tcn_handmark_live45f/strict_v1_tcn_final_stream_set_gate.md \
  --tcn-handmark-csv-benchmark-json outputs/right_conducting/selected_tcn_handmark_live45f/strict_v1_tcn_final_stream_benchmark.json \
  --tcn-handmark-csv-benchmark-md outputs/right_conducting/selected_tcn_handmark_live45f/strict_v1_tcn_final_stream_benchmark.md \
  --tcn-handmark-stream-readiness-stdin-summary-json outputs/right_conducting/selected_tcn_handmark_live45f/stdin_smoke_summary.json \
  --tcn-handmark-stream-readiness-stdin-output-jsonl outputs/right_conducting/selected_tcn_handmark_live45f/stdin_smoke_outputs.jsonl \
  --tcn-handmark-stream-readiness-json outputs/right_conducting/selected_tcn_handmark_live45f/strict_v1_tcn_final_readiness_with_output_contract.json \
  --tcn-handmark-stream-readiness-md outputs/right_conducting/selected_tcn_handmark_live45f/strict_v1_tcn_final_readiness_with_output_contract.md \
  --tcn-goal-status-strict-preflight-json outputs/right_conducting/selected_tcn_handmark_live45f/strict_v1_tcn_final_preflight.json \
  --tcn-goal-status-output-json outputs/right_conducting/selected_tcn_handmark_live45f/strict_v1_tcn_final_goal_status.json \
  --tcn-goal-status-output-md outputs/right_conducting/selected_tcn_handmark_live45f/strict_v1_tcn_final_goal_status.md \
  --tcn-goal-status-fail-on-in-progress \
  --output-json outputs/right_conducting/selected_tcn_handmark_live45f/strict_v1_tcn_final_post_arrival_goal_run.json \
  --output-md outputs/right_conducting/selected_tcn_handmark_live45f/strict_v1_tcn_final_post_arrival_goal_run.md
```

Replace `--handmark-csv-stream-csv` with any real strict transition CSV if the placeholder filename differs.

## Verification

Dry-run artifact inspection confirms:

```text
tcn_handmark_stream_readiness includes --stream-output-jsonl and --stdin-output-jsonl
tcn_goal_status consumes strict_v1_tcn_final_stream_set_gate.json
tcn_goal_status consumes strict_v1_tcn_final_readiness_with_output_contract.json
tcn_goal_status consumes strict_v1_tcn_final_preflight.json
tcn_goal_status uses --fail-on-in-progress
```

## Decision

This supersedes the older Report 89 dry-run for final strict reporting. The current selected TCN live result is still `GO` for fixed-camera supplied data and `NO_GO` for strict heldout until these roots exist and this final chain passes.

