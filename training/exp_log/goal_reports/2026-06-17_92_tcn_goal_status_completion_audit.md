# Report 92 - TCN Goal Status Completion Audit

## Purpose

Add a machine-readable completion audit for the selected TCN live runtime. The audit prevents the current fixed-camera live result from being mistaken for full strict heldout completion.

## Added Files

```text
lib/right_conducting/tcn_goal_status.py
tools/summarize_tcn_right_conducting_goal_status.py
tests/test_tcn_goal_status.py
```

Updated:

```text
tools/run_right_conducting_goal.py
tests/test_goal_command_cli.py
```

## New Goal Runner Step

Step name:

```text
tcn-goal-status
```

Command shape:

```bash
python tools/run_right_conducting_goal.py \
  --steps tcn-goal-status \
  --tcn-manifest outputs/right_conducting/selected_tcn_handmark_live45f/tcn_conducting_live_manifest.json \
  --tcn-handmark-csv-set-gate-json outputs/right_conducting/selected_tcn_handmark_live45f/alltest_2beat3beat_stream_set_gate.json \
  --tcn-handmark-csv-benchmark-json outputs/right_conducting/selected_tcn_handmark_live45f/alltest_2beat3beat_stream_benchmark.json \
  --tcn-handmark-stream-readiness-json outputs/right_conducting/selected_tcn_handmark_live45f/alltest_2beat3beat_stream_readiness_with_output_contract.json \
  --tcn-goal-status-strict-preflight-json outputs/right_conducting/selected_tcn_handmark_live45f/alltest_strict_heldout_preflight.json \
  --tcn-goal-status-output-json outputs/right_conducting/selected_tcn_handmark_live45f/tcn_goal_status_current.json \
  --tcn-goal-status-output-md outputs/right_conducting/selected_tcn_handmark_live45f/tcn_goal_status_current.md
```

Use `--tcn-goal-status-fail-on-in-progress` in CI or final reporting scripts when strict heldout must be required.

## Current Audit Result

Artifacts:

```text
outputs/right_conducting/selected_tcn_handmark_live45f/tcn_goal_status_current.json
outputs/right_conducting/selected_tcn_handmark_live45f/tcn_goal_status_current.md
outputs/right_conducting/selected_tcn_handmark_live45f/tcn_goal_status_runner_chain.json
outputs/right_conducting/selected_tcn_handmark_live45f/tcn_goal_status_runner_chain.md
```

Status:

```text
schema_version: right_conducting_tcn_goal_status_v1
status: IN_PROGRESS
live_status: GO
strict_heldout_status: NO_GO
```

Live checks all pass:

| check | value |
|---|---:|
| model_type | causal_tcn_right_arm_pose |
| tempo_acc | 1.0000 |
| gain_acc | 1.0000 |
| false_switches_per_min | 0.0000 |
| missed_switch_count | 0 |
| benchmark_p90_ms | 1.6854 |
| benchmark_headroom_ratio | 118.6673 |
| stream_rows | 216 |
| stdin_rows | 3 |
| stream_output_contract_errors | 0 |
| stdin_output_contract_errors | 0 |

Strict checks fail:

| check | status |
|---|---|
| strict_static_root_exists | false |
| strict_transition_root_exists | false |
| strict_preflight_status_go | false |
| strict_independence_go | false |
| strict_scope_go | false |
| strict_p0_complete | false |

Missing roots:

```text
dataset/strict_heldout_static_v1
dataset/strict_heldout_transitions_v1
```

## Verification

```text
python -m py_compile lib/right_conducting/tcn_goal_status.py tools/summarize_tcn_right_conducting_goal_status.py tools/run_right_conducting_goal.py tests/test_tcn_goal_status.py tests/test_goal_command_cli.py
PYTHONPATH=. python -m unittest discover -s tests -p 'test_tcn_goal_status.py' -v
PYTHONPATH=. python -m unittest discover -s tests -p 'test_goal_command_cli.py' -v
PYTHONPATH=. python -m unittest discover tests -v
```

Result:

```text
test_tcn_goal_status.py: 4 OK
test_goal_command_cli.py: 39 OK
full unittest suite: 257 OK, 56.318s
```

## Decision

The selected TCN runtime remains the correct live-facing fixed-camera model. The completion audit keeps the final objective open until strict heldout data is supplied and passes the post-arrival chain.
