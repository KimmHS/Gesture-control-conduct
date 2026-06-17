# Report 115 - Current Strict Data Contract Snapshot

## Purpose

Report 114 added the strict data contract gate. This report runs that gate against the current workspace state and records the expected `NO_GO` result while strict heldout roots are still absent.

## Command

```bash
python tools/run_right_conducting_goal.py \
  --steps heldout-independence,strict-heldout-scope,strict-heldout-missing-checklist,strict-heldout-data-contract \
  --heldout-train-manifests outputs/right_conducting/recordings_staged_static80_transitions_manifest.json \
  --heldout-eval-roots dataset/strict_heldout_static_v1,dataset/strict_heldout_transitions_v1 \
  --heldout-independence-output-json outputs/right_conducting/tcn_alltest_latest/current_strict_heldout_independence.json \
  --heldout-independence-output-md outputs/right_conducting/tcn_alltest_latest/current_strict_heldout_independence.md \
  --heldout-scope-output-json outputs/right_conducting/tcn_alltest_latest/current_strict_heldout_scope.json \
  --heldout-scope-output-md outputs/right_conducting/tcn_alltest_latest/current_strict_heldout_scope.md \
  --heldout-missing-output-json outputs/right_conducting/tcn_alltest_latest/current_strict_missing_checklist.json \
  --heldout-missing-output-md outputs/right_conducting/tcn_alltest_latest/current_strict_missing_checklist.md \
  --heldout-data-contract-output-json outputs/right_conducting/tcn_alltest_latest/current_strict_data_contract.json \
  --heldout-data-contract-output-md outputs/right_conducting/tcn_alltest_latest/current_strict_data_contract.md
```

## Artifacts

```text
outputs/right_conducting/tcn_alltest_latest/current_strict_heldout_independence.json
outputs/right_conducting/tcn_alltest_latest/current_strict_heldout_independence.md
outputs/right_conducting/tcn_alltest_latest/current_strict_heldout_scope.json
outputs/right_conducting/tcn_alltest_latest/current_strict_heldout_scope.md
outputs/right_conducting/tcn_alltest_latest/current_strict_missing_checklist.json
outputs/right_conducting/tcn_alltest_latest/current_strict_missing_checklist.md
outputs/right_conducting/tcn_alltest_latest/current_strict_data_contract.json
outputs/right_conducting/tcn_alltest_latest/current_strict_data_contract.md
outputs/right_conducting/tcn_alltest_latest/current_strict_data_contract_goal_run.json
outputs/right_conducting/tcn_alltest_latest/current_strict_data_contract_goal_run.md
```

## Result

Current strict data contract:

```text
status: NO_GO
p0_required: 8
p0_present: 0
p0_session_count: 0
missing_csv_count: 0
artifact_incomplete_count: 0
next_action: fix strict heldout P0 scope before stream scoring
```

Current strict scope:

```text
status: NO_GO
missing_heldout_roots:
  dataset/strict_heldout_static_v1
  dataset/strict_heldout_transitions_v1
priority_summary.P0: required 8 / present 0 / missing 8
```

The CSV sibling gate is working, but it cannot inspect CSV siblings yet because no matched P0 strict sessions exist. Once P0 sessions are present, the same gate will require each matched processed session directory to have a same-stem raw handmark CSV sibling.

## Checks

Key failed checks:

```text
strict_scope_p0_complete: false
p0_case_count: 0 == 8 -> false
p0_session_csv_siblings_present: no matched P0 sessions to score
```

## Verification

Focused test:

```text
PYTHONPATH=. python -m unittest discover -s tests -p 'test_strict_data_contract.py' -v
Ran 4 tests in 0.072s
OK
```

Full regression:

```text
PYTHONPATH=. python -m unittest discover tests -v
Ran 275 tests in 57.475s
OK
```

## Goal Status

The live model and runtime remain ready for the supplied fixed-camera scope, but the full goal is still `IN_PROGRESS` because strict heldout data is absent.
