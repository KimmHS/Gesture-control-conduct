# Report 98 - Full Test Rerun

## Purpose

Rerun the full local test suite after the Report 97 strict release-precheck chain update, then recheck the selected TCN live release and goal status artifacts.

## Commands

```bash
PYTHONPATH=. python -m unittest discover tests -v > /tmp/motionbert_full_unittest_report97.log 2>&1

python tools/check_tcn_live_release_manifest.py \
  --manifest outputs/right_conducting/selected_tcn_handmark_live45f/tcn_live_release_manifest.json \
  --output-json outputs/right_conducting/selected_tcn_handmark_live45f/tcn_live_release_manifest_validation_report98_fulltest.json \
  --output-md outputs/right_conducting/selected_tcn_handmark_live45f/tcn_live_release_manifest_validation_report98_fulltest.md

python tools/summarize_tcn_right_conducting_goal_status.py \
  --manifest outputs/right_conducting/selected_tcn_handmark_live45f/tcn_conducting_live_manifest.json \
  --gate-json outputs/right_conducting/selected_tcn_handmark_live45f/alltest_2beat3beat_stream_set_gate.json \
  --readiness-json outputs/right_conducting/selected_tcn_handmark_live45f/alltest_2beat3beat_stream_readiness_with_output_contract.json \
  --benchmark-json outputs/right_conducting/selected_tcn_handmark_live45f/alltest_2beat3beat_stream_benchmark.json \
  --strict-preflight-json outputs/right_conducting/selected_tcn_handmark_live45f/strict_heldout_preflight.json \
  --strict-static-root dataset/strict_heldout_static_v1 \
  --strict-transition-root dataset/strict_heldout_transitions_v1 \
  --output-json outputs/right_conducting/selected_tcn_handmark_live45f/tcn_goal_status_report98_fulltest.json \
  --output-md outputs/right_conducting/selected_tcn_handmark_live45f/tcn_goal_status_report98_fulltest.md
```

## Results

```text
full unittest suite: 261 OK, 56.241s
release manifest validation: GO, error_count 0
TCN goal status: IN_PROGRESS
live status: GO
strict heldout status: NO_GO
```

Selected live metrics from the goal status rerun:

```text
tempo_acc: 1.0000
gain_acc: 1.0000
false_switches_per_min: 0.0000
missed_switch_count: 0
benchmark_p90_ms: 1.6854
stream_output_contract_errors: 0
stdin_output_contract_errors: 0
```

## Decision

All runnable local tests and TCN live release checks pass. The remaining blocker is not code or selected-bundle readiness; it is the missing strict heldout roots:

```text
dataset/strict_heldout_static_v1
dataset/strict_heldout_transitions_v1
```

Do not mark the full goal complete until those roots are supplied and the strict post-arrival chain passes.
