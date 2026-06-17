# Report 116 - Current Status Includes Data Contract

## Purpose

Report 114 added the strict data contract gate and Report 115 recorded the current `NO_GO` data contract snapshot. This report connects that gate into the TCN current-status dashboard so final status snapshots include the data-contract result and artifact path.

## Updated Code

```text
lib/right_conducting/tcn_current_status.py
tools/export_tcn_current_status.py
tools/run_right_conducting_goal.py
scripts/run_tcn_strict_post_arrival_goal.sh
tests/test_tcn_current_status.py
tests/test_goal_command_cli.py
```

## New Snapshot Fields

`current_status_snapshot.json` and `current_status_runner_snapshot.json` now include:

```text
strict_data_contract.status
strict_data_contract.p0_required
strict_data_contract.p0_present
strict_data_contract.p0_session_count
strict_data_contract.missing_csv_count
strict_data_contract.artifact_incomplete_count
strict_data_contract.next_action
artifacts.strict_data_contract_json
```

Current value:

```text
strict_data_contract.status: NO_GO
strict_data_contract.p0_required: 8
strict_data_contract.p0_present: 0
strict_data_contract.p0_session_count: 0
strict_data_contract.missing_csv_count: 0
strict_data_contract.next_action: fix strict heldout P0 scope before stream scoring
```

## Updated Artifacts

```text
outputs/right_conducting/tcn_alltest_latest/current_status_snapshot.json
outputs/right_conducting/tcn_alltest_latest/current_status_snapshot.md
outputs/right_conducting/tcn_alltest_latest/current_status_runner_snapshot.json
outputs/right_conducting/tcn_alltest_latest/current_status_runner_snapshot.md
```

The markdown snapshots now include:

```text
## Strict Data Contract
```

## Wrapper Wiring

The strict post-arrival wrapper now passes:

```text
--tcn-current-status-data-contract-json outputs/right_conducting/selected_tcn_handmark_live45f/strict_v1_tcn_release_precheck_data_contract.json
```

to the final `tcn-current-status` step.

## Verification

Focused tests:

```text
PYTHONPATH=. python -m unittest discover -s tests -p 'test_tcn_current_status.py' -v
Ran 4 tests in 0.127s
OK

PYTHONPATH=. python -m unittest discover -s tests -p 'test_goal_command_cli.py' -v
Ran 44 tests in 2.887s
OK
```

Snapshot assertion:

```text
tcn_current_status_data_contract_assertions_ok
```

Full regression:

```text
PYTHONPATH=. python -m unittest discover tests -v
Ran 275 tests in 58.739s
OK
```

## Goal Status

The dashboard now exposes the strict data-contract blocker directly. The full goal is still `IN_PROGRESS` because strict heldout roots are absent.
