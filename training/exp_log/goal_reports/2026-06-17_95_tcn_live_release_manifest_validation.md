# Report 95 - TCN Live Release Manifest Validation

## Purpose

Add an automatic validator for the selected TCN live release manifest. Report 94 created the handoff manifest and runbook; this report makes the handoff checkable.

## Added Files

```text
lib/right_conducting/tcn_release_manifest.py
tools/check_tcn_live_release_manifest.py
tests/test_tcn_release_manifest.py
```

## Selected Validation Artifacts

```text
outputs/right_conducting/selected_tcn_handmark_live45f/tcn_live_release_manifest_validation.json
outputs/right_conducting/selected_tcn_handmark_live45f/tcn_live_release_manifest_validation.md
```

Result:

```text
schema_version: right_conducting_tcn_live_release_validation_v1
status: GO
error_count: 0
release_status: LIVE_READY_STRICT_HELDOUT_PENDING
live_status: GO
strict_heldout_status: NO_GO
```

## What The Validator Checks

```text
release schema version
live_status / strict_heldout_status
model manifest, checkpoint, structure paths
checkpoint SHA256
model manifest SHA256
live manifest model_type/window/stride/fps/bpm_bins
live input entrypoint and output schema
score/gate/benchmark/readiness/goal-status/contract artifact paths
gate/readiness/goal-status/stream contract/stdin contract status
selected metric consistency against evidence files
strict blocker roots still absent
strict final dry-run path exists
```

## Command

```bash
python tools/check_tcn_live_release_manifest.py \
  --manifest outputs/right_conducting/selected_tcn_handmark_live45f/tcn_live_release_manifest.json \
  --output-json outputs/right_conducting/selected_tcn_handmark_live45f/tcn_live_release_manifest_validation.json \
  --output-md outputs/right_conducting/selected_tcn_handmark_live45f/tcn_live_release_manifest_validation.md \
  --fail-on-no-go
```

## Verification

```text
python -m py_compile lib/right_conducting/tcn_release_manifest.py tools/check_tcn_live_release_manifest.py tests/test_tcn_release_manifest.py
PYTHONPATH=. python -m unittest discover -s tests -p 'test_tcn_release_manifest.py' -v
PYTHONPATH=. python -m unittest discover tests -v
```

Result:

```text
test_tcn_release_manifest.py: 3 OK
full unittest suite: 260 OK, 57.998s
```

## Decision

The selected TCN live release package is internally consistent and can be handed off as the current fixed-camera runtime. Final goal completion remains open because strict heldout roots are still missing.
