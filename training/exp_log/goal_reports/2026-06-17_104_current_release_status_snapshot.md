# Report 104 - Current Release Status Snapshot

## Purpose

Re-run the selected TCN release validation and TCN goal status audit after the strict post-arrival script/test updates. This confirms that the selected live bundle remains internally consistent and that the remaining blocker is still strict heldout data.

## Commands

```bash
python tools/check_tcn_live_release_manifest.py \
  --manifest outputs/right_conducting/selected_tcn_handmark_live45f/tcn_live_release_manifest.json \
  --output-json outputs/right_conducting/selected_tcn_handmark_live45f/tcn_live_release_manifest_validation_report104.json \
  --output-md outputs/right_conducting/selected_tcn_handmark_live45f/tcn_live_release_manifest_validation_report104.md

python tools/summarize_tcn_right_conducting_goal_status.py \
  --manifest outputs/right_conducting/selected_tcn_handmark_live45f/tcn_conducting_live_manifest.json \
  --gate-json outputs/right_conducting/selected_tcn_handmark_live45f/alltest_2beat3beat_stream_set_gate.json \
  --readiness-json outputs/right_conducting/selected_tcn_handmark_live45f/alltest_2beat3beat_stream_readiness_with_output_contract.json \
  --benchmark-json outputs/right_conducting/selected_tcn_handmark_live45f/alltest_2beat3beat_stream_benchmark.json \
  --strict-preflight-json outputs/right_conducting/selected_tcn_handmark_live45f/report99_strict_heldout_preflight.json \
  --strict-static-root dataset/strict_heldout_static_v1 \
  --strict-transition-root dataset/strict_heldout_transitions_v1 \
  --output-json outputs/right_conducting/selected_tcn_handmark_live45f/tcn_goal_status_report104.json \
  --output-md outputs/right_conducting/selected_tcn_handmark_live45f/tcn_goal_status_report104.md
```

## Results

```text
release validation: GO
release error_count: 0
release_status: LIVE_READY_STRICT_HELDOUT_PENDING
goal status: IN_PROGRESS
live_status: GO
strict_heldout_status: NO_GO
```

Selected live metrics:

```text
tempo_acc: 1.0000
gain_acc: 1.0000
false_switches_per_min: 0.0000
missed_switch_count: 0
benchmark_p90_ms: 1.6854
stream_output_contract_errors: 0
stdin_output_contract_errors: 0
```

Strict preflight remains:

```text
status: NO_GO
independence_status: NO_GO
scope_status: NO_GO
p0_complete: false
```

## Verification Context

Latest full test run from Report 103:

```text
Ran 263 tests in 58.555s
OK
```

## Decision

The selected TCN live release remains valid and runnable for the fixed-camera deployment-fit setup. The full goal remains active because strict independent heldout roots are still absent:

```text
dataset/strict_heldout_static_v1
dataset/strict_heldout_transitions_v1
```

After those roots arrive, run:

```bash
scripts/run_tcn_strict_post_arrival_goal.sh --dry-run
scripts/run_tcn_strict_post_arrival_goal.sh
```
