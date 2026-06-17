# Report 96 - TCN Release Validation Goal Runner Step

## Purpose

Attach the TCN live release manifest validation to the reproducible goal runner. Report 95 added the validator; this report makes it callable as a pipeline step.

## Added Step

```text
tcn-release-validate
```

New runner flags:

```text
--tcn-release-manifest
--tcn-release-validation-json
--tcn-release-validation-md
--tcn-release-validation-fail-on-no-go
```

## Selected Execution

Command:

```bash
python tools/run_right_conducting_goal.py \
  --steps tcn-release-validate \
  --tcn-release-manifest outputs/right_conducting/selected_tcn_handmark_live45f/tcn_live_release_manifest.json \
  --tcn-release-validation-json outputs/right_conducting/selected_tcn_handmark_live45f/tcn_live_release_manifest_validation.json \
  --tcn-release-validation-md outputs/right_conducting/selected_tcn_handmark_live45f/tcn_live_release_manifest_validation.md \
  --tcn-release-validation-fail-on-no-go \
  --output-json outputs/right_conducting/selected_tcn_handmark_live45f/tcn_release_validation_goal_chain.json \
  --output-md outputs/right_conducting/selected_tcn_handmark_live45f/tcn_release_validation_goal_chain.md
```

Artifacts:

```text
outputs/right_conducting/selected_tcn_handmark_live45f/tcn_release_validation_goal_chain.json
outputs/right_conducting/selected_tcn_handmark_live45f/tcn_release_validation_goal_chain.md
```

Result:

```text
tcn_release_validate: ok
release validation status: GO
error_count: 0
```

## Verification

```text
python -m py_compile tools/run_right_conducting_goal.py tests/test_goal_command_cli.py
PYTHONPATH=. python -m unittest discover -s tests -p 'test_goal_command_cli.py' -v
PYTHONPATH=. python -m unittest discover tests -v
```

Result:

```text
test_goal_command_cli.py: 40 OK
full unittest suite: 261 OK, 56.540s
```

## Decision

The selected TCN release package can now be validated either directly with `tools/check_tcn_live_release_manifest.py` or through the goal runner. Strict heldout completion remains pending.
