# Report 119 - TCN Handoff And Model Card Refresh

## Purpose

The selected TCN live bundle and latest score artifacts were already valid, but the top of the handoff runbook and model card still pointed at older Report 106 / `alltest_2beat3beat_*` evidence. This report records the refresh so the first documents a user opens now point to the latest Report 117/118 artifacts.

## Updated Files

```text
docs/exp/tcn_live_handoff_runbook.md
docs/exp/right_hand_conducting_model_card.md
```

## Handoff Runbook Updates

The runbook now points to:

```text
goal status: outputs/right_conducting/tcn_alltest_latest/tcn_goal_status_fulltest_latest.json
score gate: outputs/right_conducting/tcn_alltest_latest/stream_set_gate_fulltest_latest.json
readiness: outputs/right_conducting/tcn_alltest_latest/stream_readiness.json
current status: outputs/right_conducting/tcn_alltest_latest/current_status_fulltest_latest.json
release validation: outputs/right_conducting/selected_tcn_handmark_live45f/tcn_live_release_manifest_validation_fulltest_latest.json
```

The current evidence table now distinguishes:

```text
discovered raw CSV files: 15
scoreable processed sessions: 11
```

## Model Card Updates

The selected TCN score block now points to:

```text
report: docs/exp/goal_reports/2026-06-17_117_full_test_release_and_status_rerun.md
score: outputs/right_conducting/tcn_alltest_latest/stream_set_score_fulltest_latest.json
gate: outputs/right_conducting/tcn_alltest_latest/stream_set_gate_fulltest_latest.json
goal_status: outputs/right_conducting/tcn_alltest_latest/tcn_goal_status_fulltest_latest.json
current_status: outputs/right_conducting/tcn_alltest_latest/current_status_fulltest_latest.json
```

The lower TCN status block now also includes the latest fulltest artifacts and the `15 raw CSV / 11 scoreable sessions` distinction.

## Verification

Artifact path check:

```text
latest_handoff_model_card_artifact_paths_exist
```

Stale latest-path search:

```text
No stale top-level references found for:
  tcn_goal_status_current
  tcn_live_release_manifest_validation_latest
  current_status_runner_snapshot
  latest all-test csv_count: 11
  stream_set_score.json / stream_set_gate.json in the selected TCN score block
```

Document assertion:

```text
handoff_model_card_latest_assertions_ok
```

## Current Status

This is a documentation handoff refresh. It does not change the selected TCN checkpoint or score values. Current state remains:

```text
selected TCN live path: GO on supplied fixed-camera set
release validation: GO
strict heldout: NO_GO, P0 0/8
overall goal: IN_PROGRESS
```
