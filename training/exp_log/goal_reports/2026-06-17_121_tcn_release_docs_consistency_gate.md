# Report 121 - TCN Release Docs Consistency Gate

## Purpose

Reports 117-120 refreshed the selected TCN score, handoff, model card, submission format, and presentation summary. This report adds an executable consistency gate so those documents can be checked automatically against the latest TCN fulltest artifacts.

## Added Files

```text
lib/right_conducting/tcn_release_docs.py
tools/check_tcn_release_docs.py
tests/test_tcn_release_docs.py
```

## What The Gate Checks

The checker validates:

```text
score doc exists and points to stream_set_score_fulltest_latest / stream_set_gate_fulltest_latest
model card exists and points to selected_tcn_handmark_live45f + latest fulltest status artifacts
handoff runbook exists and points to latest goal/gate/current-status/release-validation artifacts
submission format exists and describes selected causal TCN, not MotionBERT-first pipeline
presentation summary exists and references Report 117/119 plus latest score/current-status artifacts
gate JSON is GO with 15 raw CSV / 11 scoreable sessions / margin 3s
current status is IN_PROGRESS with live GO and strict heldout NO_GO
release validation is GO
known stale top-level references are absent
```

## Command

```bash
python tools/check_tcn_release_docs.py \
  --output-json outputs/right_conducting/tcn_alltest_latest/release_docs_check.json \
  --output-md outputs/right_conducting/tcn_alltest_latest/release_docs_check.md \
  --fail-on-no-go
```

## Current Result

```text
status: GO
check_count: 63
failed_count: 0
```

Artifacts:

```text
outputs/right_conducting/tcn_alltest_latest/release_docs_check.json
outputs/right_conducting/tcn_alltest_latest/release_docs_check.md
```

## Verification

Focused tests:

```text
PYTHONPATH=. python -m unittest discover -s tests -p 'test_tcn_release_docs.py' -v
Ran 4 tests in 0.137s
OK
```

Compile check:

```text
python -m py_compile lib/right_conducting/tcn_release_docs.py tools/check_tcn_release_docs.py
OK
```

Live repo check:

```text
python tools/check_tcn_release_docs.py --output-json outputs/right_conducting/tcn_alltest_latest/release_docs_check.json --output-md outputs/right_conducting/tcn_alltest_latest/release_docs_check.md --fail-on-no-go
status: GO
check_count: 63
failed_count: 0
```

## Current Status

This adds a maintainability/readiness gate only. It does not change model weights or scores. The selected TCN live path remains `GO` on supplied fixed-camera data. The full goal remains `IN_PROGRESS` because strict independent heldout roots are still absent.
