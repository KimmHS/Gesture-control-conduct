# Report 107 - Current Status Exporter

## Purpose

Manual status pages were useful, but the current TCN live state should also be reproducible from the authoritative JSON artifacts. This report adds a small exporter that builds a current status snapshot from:

```text
TCN goal status JSON
TCN release validation JSON
strict heldout preflight JSON
```

This keeps the dashboard aligned with the actual score/release/preflight artifacts.

## Added Files

```text
lib/right_conducting/tcn_current_status.py
tools/export_tcn_current_status.py
tests/test_tcn_current_status.py
```

## Command

```bash
python tools/export_tcn_current_status.py \
  --goal-status-json outputs/right_conducting/tcn_alltest_latest/tcn_goal_status.json \
  --release-validation-json outputs/right_conducting/selected_tcn_handmark_live45f/tcn_live_release_manifest_validation_latest.json \
  --strict-preflight-json outputs/right_conducting/selected_tcn_handmark_live45f/strict_v1_tcn_release_precheck_preflight.json \
  --output-json outputs/right_conducting/tcn_alltest_latest/current_status_snapshot.json \
  --output-md outputs/right_conducting/tcn_alltest_latest/current_status_snapshot.md
```

## Output

```text
outputs/right_conducting/tcn_alltest_latest/current_status_snapshot.json
outputs/right_conducting/tcn_alltest_latest/current_status_snapshot.md
```

Snapshot result:

```text
schema_version: right_conducting_tcn_current_status_v1
status: IN_PROGRESS
live_status: GO
release_validation_status: GO
strict_heldout_status: NO_GO
blocker: missing strict heldout roots or required P0 coverage
```

Selected metrics:

```text
tempo_acc: 1.0000
gain_acc: 1.0000
false_switches_per_min: 0.0000
missed_switch_count: 0
switch_delay_p90_s: 0.0000
benchmark_p90_ms: 1.9984
benchmark_headroom_ratio: 100.0821
stream_rows: 216
stdin_rows: 3
stream_output_contract_errors: 0
stdin_output_contract_errors: 0
```

Strict preflight:

```text
status: NO_GO
independence_status: NO_GO
scope_status: NO_GO
p0_complete: false
P0 required / present / missing: 8 / 0 / 8
next_action: fix heldout independence before scoring strict replay
```

## Verification

Syntax:

```bash
python -m py_compile \
  lib/right_conducting/tcn_current_status.py \
  tools/export_tcn_current_status.py \
  tests/test_tcn_current_status.py
```

Focused tests:

```bash
PYTHONPATH=. python -m unittest discover -s tests -p 'test_tcn_current_status.py' -v
```

Result:

```text
Ran 4 tests in 0.121s
OK
```

Full regression suite:

```bash
PYTHONPATH=. python -m unittest discover tests -v
```

Result:

```text
Ran 268 tests in 57.367s
OK
```

## Interpretation

The current live-facing TCN bundle remains runnable and release-valid:

```text
live/runtime: GO
release validation: GO
```

The full goal remains incomplete because strict independent heldout evidence is still missing:

```text
strict heldout: NO_GO
missing roots:
  dataset/strict_heldout_static_v1
  dataset/strict_heldout_transitions_v1
```

## Next Action

When strict heldout data is supplied, run:

```bash
scripts/run_tcn_strict_post_arrival_goal.sh --dry-run
scripts/run_tcn_strict_post_arrival_goal.sh
python tools/export_tcn_current_status.py
```
