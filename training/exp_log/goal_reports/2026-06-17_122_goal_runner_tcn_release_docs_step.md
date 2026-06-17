# Report 122 - Goal Runner TCN Release Docs Step

## Purpose

Report 121 added `tools/check_tcn_release_docs.py`, but it was only runnable as a standalone checker. This report connects that checker to the reproducible goal runner so the selected TCN release documentation consistency gate can be executed through the same command surface as the rest of the project.

## Updated Files

```text
tools/run_right_conducting_goal.py
tests/test_goal_command_cli.py
```

## New Goal Runner Step

Step name:

```text
tcn-release-docs
```

Example:

```bash
python tools/run_right_conducting_goal.py \
  --steps tcn-release-docs \
  --tcn-release-docs-output-json outputs/right_conducting/tcn_alltest_latest/release_docs_goal_run.json \
  --tcn-release-docs-output-md outputs/right_conducting/tcn_alltest_latest/release_docs_goal_run.md \
  --tcn-release-docs-fail-on-no-go \
  --output-json outputs/right_conducting/tcn_alltest_latest/release_docs_goal_chain.json \
  --output-md outputs/right_conducting/tcn_alltest_latest/release_docs_goal_chain.md
```

The step calls:

```text
tools/check_tcn_release_docs.py
```

with the latest selected TCN score/status/doc defaults.

## New CLI Options

```text
--tcn-release-docs-score-doc
--tcn-release-docs-model-card
--tcn-release-docs-handoff
--tcn-release-docs-submission
--tcn-release-docs-presentation
--tcn-release-docs-gate-json
--tcn-release-docs-current-status-json
--tcn-release-docs-release-validation-json
--tcn-release-docs-output-json
--tcn-release-docs-output-md
--tcn-release-docs-fail-on-no-go
```

## Artifacts

Dry-run:

```text
outputs/right_conducting/tcn_alltest_latest/release_docs_goal_dryrun.json
outputs/right_conducting/tcn_alltest_latest/release_docs_goal_dryrun.md
```

Executed run:

```text
outputs/right_conducting/tcn_alltest_latest/release_docs_goal_run.json
outputs/right_conducting/tcn_alltest_latest/release_docs_goal_run.md
outputs/right_conducting/tcn_alltest_latest/release_docs_goal_chain.json
outputs/right_conducting/tcn_alltest_latest/release_docs_goal_chain.md
```

Current result:

```text
status: GO
check_count: 63
failed_count: 0
```

## Verification

Focused goal runner tests:

```text
PYTHONPATH=. python -m unittest discover -s tests -p 'test_goal_command_cli.py' -v
Ran 45 tests in 2.942s
OK
```

Focused release-doc tests:

```text
PYTHONPATH=. python -m unittest discover -s tests -p 'test_tcn_release_docs.py' -v
Ran 4 tests in 0.132s
OK
```

Goal runner assertion:

```text
tcn_release_docs_goal_runner_assertions_ok
```

Full regression:

```text
PYTHONPATH=. python -m unittest discover tests -v
Ran 281 tests in 58.072s
OK
```

## Current Status

The selected TCN live/release documentation gate is now part of the reproducible goal runner. This still does not complete the full goal because strict independent heldout roots are absent.
