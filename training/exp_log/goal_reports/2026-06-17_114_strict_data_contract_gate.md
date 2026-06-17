# Report 114 - Strict Data Contract Gate

## Purpose

Report 113 documented the strict heldout data contract. This report turns the CSV-sibling part of that contract into an executable gate and inserts it into the strict post-arrival chain before TCN stream scoring.

## Added Code

```text
lib/right_conducting/strict_data_contract.py
tools/check_right_conducting_strict_data_contract.py
tests/test_strict_data_contract.py
```

## Updated Code

```text
tools/run_right_conducting_goal.py
scripts/run_tcn_strict_post_arrival_goal.sh
tests/test_goal_command_cli.py
```

## New Gate Behavior

The new gate reads the strict scope audit JSON and checks:

```text
scope_json_present
strict_scope_p0_complete
p0_case_count
p0_session_csv_siblings_present
p0_artifacts_complete
```

The key added protection is:

```text
Each matched P0 processed session directory must have a raw handmark CSV sibling with the same stem.
```

Example:

```text
dataset/strict_heldout_transitions_v1/P0_transition_120_to_80_to_120_beat2_small.csv
dataset/strict_heldout_transitions_v1/P0_transition_120_to_80_to_120_beat2_small/
```

## Updated Strict Chain

The strict post-arrival wrapper now runs 13 steps:

```text
1. tcn-release-validate
2. heldout-independence
3. strict-heldout-scope
4. strict-heldout-missing-checklist
5. strict-heldout-data-contract
6. strict-heldout-preflight
7. tcn-handmark-csv-stream
8. tcn-handmark-csv-set-score
9. tcn-handmark-csv-set-gate
10. tcn-handmark-csv-benchmark
11. tcn-handmark-stream-readiness
12. tcn-goal-status
13. tcn-current-status
```

The new step is fail-fast:

```text
strict-heldout-data-contract: --fail-on-no-go
```

Dry-run artifact:

```text
outputs/right_conducting/selected_tcn_handmark_live45f/strict_v1_tcn_release_precheck_post_arrival_goal_run.json
```

New expected output:

```text
outputs/right_conducting/selected_tcn_handmark_live45f/strict_v1_tcn_release_precheck_data_contract.json
outputs/right_conducting/selected_tcn_handmark_live45f/strict_v1_tcn_release_precheck_data_contract.md
```

## Verification

Focused tests:

```text
PYTHONPATH=. python -m unittest discover -s tests -p 'test_strict_data_contract.py' -v
Ran 3 tests in 0.069s
OK

PYTHONPATH=. python -m unittest discover -s tests -p 'test_goal_command_cli.py' -v
Ran 44 tests in 2.870s
OK
```

Dry-run assertion:

```text
strict_post_arrival_13step_data_contract_dryrun_assertions_ok
step_count: 13
data_contract_step: strict_heldout_data_contract
data_contract_output: outputs/right_conducting/selected_tcn_handmark_live45f/strict_v1_tcn_release_precheck_data_contract.json
```

Full regression:

```text
PYTHONPATH=. python -m unittest discover tests -v
Ran 274 tests in 59.183s
OK
```

## Goal Status

This improves the final strict data intake gate, but it does not complete the goal. Strict heldout roots are still absent, so the goal remains `IN_PROGRESS`.
