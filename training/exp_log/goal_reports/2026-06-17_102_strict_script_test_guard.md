# Report 102 - Strict Script Test Guard

## Purpose

Add a regression test for the strict post-arrival script introduced in Report 101. The goal is to keep the final strict chain reproducible as code changes: release validation must remain first, strict scoring must remain gated, and TCN goal status must remain last.

## Code Change

Updated:

```text
tests/test_goal_command_cli.py
```

Added test:

```text
test_tcn_strict_post_arrival_script_dry_run_contract
```

The test runs:

```bash
bash scripts/run_tcn_strict_post_arrival_goal.sh --dry-run
```

with temporary environment overrides:

```text
PYTHON
SELECTED_ROOT
STRICT_STATIC_ROOT
STRICT_TRANSITION_ROOT
STRICT_STREAM_CSV
TRAIN_MANIFEST
DEVICE
```

It then reads the generated dry-run JSON and checks:

```text
dry_run == true
command_count == 11
first step == tcn_release_validate
last step == tcn_goal_status
all generated rows are dry_run
strict roots come from env overrides
strict stream CSV override is present in the generated command
--fail-on-no-go is present
--fail-on-in-progress is present
```

## Verification

Focused verification:

```bash
python -m py_compile tests/test_goal_command_cli.py tools/run_right_conducting_goal.py
bash -n scripts/run_tcn_strict_post_arrival_goal.sh
PYTHONPATH=. python -m unittest discover -s tests -p 'test_goal_command_cli.py' -v
```

Result:

```text
test_goal_command_cli.py: 41 OK
```

Full verification:

```bash
PYTHONPATH=. python -m unittest discover tests -v
```

Result:

```text
Ran 262 tests in 56.763s
OK
```

## Decision

The strict post-arrival script is now guarded by the regular unit test suite. This does not complete the active goal because strict heldout data is still absent, but it reduces the risk that the final post-arrival command drifts before data arrives.
