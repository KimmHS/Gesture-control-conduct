# Report 108 - TCN Current Status Goal Runner Step

## Purpose

Report 107 added `tools/export_tcn_current_status.py`. This report wires that exporter into the reproducible goal runner so the current dashboard can be generated from the same command surface as the rest of the experiment.

## Added Runner Step

```text
step: tcn-current-status
runner: tools/run_right_conducting_goal.py
command: tools/export_tcn_current_status.py
```

New CLI flags:

```text
--tcn-current-status-goal-json
--tcn-current-status-release-validation-json
--tcn-current-status-strict-preflight-json
--tcn-current-status-output-json
--tcn-current-status-output-md
```

Default dependency resolution:

```text
goal json: --tcn-goal-status-output-json
release validation json: --tcn-release-validation-json
strict preflight json: --tcn-goal-status-strict-preflight-json
```

## Dry Run

```bash
python tools/run_right_conducting_goal.py \
  --dry-run \
  --steps tcn-current-status \
  --tcn-goal-status-output-json outputs/right_conducting/tcn_alltest_latest/tcn_goal_status.json \
  --tcn-release-validation-json outputs/right_conducting/selected_tcn_handmark_live45f/tcn_live_release_manifest_validation_latest.json \
  --tcn-goal-status-strict-preflight-json outputs/right_conducting/selected_tcn_handmark_live45f/strict_v1_tcn_release_precheck_preflight.json \
  --tcn-current-status-output-json outputs/right_conducting/tcn_alltest_latest/current_status_runner_snapshot.json \
  --tcn-current-status-output-md outputs/right_conducting/tcn_alltest_latest/current_status_runner_snapshot.md \
  --output-json outputs/right_conducting/tcn_alltest_latest/current_status_runner_dryrun.json \
  --output-md outputs/right_conducting/tcn_alltest_latest/current_status_runner_dryrun.md
```

Result:

```text
dry_run: true
step: tcn_current_status
status: dry_run
```

## Actual Run

```bash
python tools/run_right_conducting_goal.py \
  --steps tcn-current-status \
  --tcn-goal-status-output-json outputs/right_conducting/tcn_alltest_latest/tcn_goal_status.json \
  --tcn-release-validation-json outputs/right_conducting/selected_tcn_handmark_live45f/tcn_live_release_manifest_validation_latest.json \
  --tcn-goal-status-strict-preflight-json outputs/right_conducting/selected_tcn_handmark_live45f/strict_v1_tcn_release_precheck_preflight.json \
  --tcn-current-status-output-json outputs/right_conducting/tcn_alltest_latest/current_status_runner_snapshot.json \
  --tcn-current-status-output-md outputs/right_conducting/tcn_alltest_latest/current_status_runner_snapshot.md \
  --output-json outputs/right_conducting/tcn_alltest_latest/current_status_runner_chain.json \
  --output-md outputs/right_conducting/tcn_alltest_latest/current_status_runner_chain.md
```

Artifacts:

```text
outputs/right_conducting/tcn_alltest_latest/current_status_runner_snapshot.json
outputs/right_conducting/tcn_alltest_latest/current_status_runner_snapshot.md
outputs/right_conducting/tcn_alltest_latest/current_status_runner_chain.json
outputs/right_conducting/tcn_alltest_latest/current_status_runner_chain.md
```

Snapshot result:

```text
schema_version: right_conducting_tcn_current_status_v1
status: IN_PROGRESS
live_status: GO
release_validation_status: GO
strict_heldout_status: NO_GO
blocker: missing strict heldout roots or required P0 coverage
P0 required / present / missing: 8 / 0 / 8
```

## Verification

Syntax:

```bash
python -m py_compile tools/run_right_conducting_goal.py tests/test_goal_command_cli.py
```

Focused runner tests:

```bash
PYTHONPATH=. python -m unittest discover -s tests -p 'test_goal_command_cli.py' -v
```

Result:

```text
Ran 43 tests in 2.912s
OK
```

Full regression suite:

```bash
PYTHONPATH=. python -m unittest discover tests -v
```

Result:

```text
Ran 270 tests in 45.090s
OK
```

## Interpretation

The current status dashboard is now available in both forms:

```text
standalone: python tools/export_tcn_current_status.py
goal runner: python tools/run_right_conducting_goal.py --steps tcn-current-status
```

The current model state remains unchanged:

```text
live/runtime: GO
release validation: GO
strict heldout: NO_GO
goal: IN_PROGRESS
```

The remaining required evidence is still strict independent heldout data.
