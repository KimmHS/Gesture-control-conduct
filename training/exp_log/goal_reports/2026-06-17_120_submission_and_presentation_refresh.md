# Report 120 - Submission And Presentation Refresh

## Purpose

The handoff runbook and model card now point to the selected TCN bundle and latest fulltest artifacts. This report updates the higher-level submission and presentation documents so they describe the same current state instead of the older MotionBERT-first plan.

## Updated Files

```text
docs/exp/final_report_submission_format.md
docs/exp/presentation_training_summary.md
```

## Submission Format Updates

`final_report_submission_format.md` now states that the current selected live model is:

```text
causal TCN right-arm pose classifier
```

The deep-learning pipeline is now:

```text
webcam / handmark CSV stream
  -> right shoulder / right elbow / right wrist
  -> H36M17 right-arm masked sequence
  -> sliding window [B, 45, 17, 3]
  -> causal TCN
  -> tempo class / gain class
  -> live smoother
  -> MIDI tempo / velocity / CC11
```

MotionBERT-Lite is kept as comparison / research baseline, not the selected current live model.

## Current Result Added

The final report format now includes a `Current Selected TCN Result` section with:

```text
score: outputs/right_conducting/tcn_alltest_latest/stream_set_score_fulltest_latest.json
gate: outputs/right_conducting/tcn_alltest_latest/stream_set_gate_fulltest_latest.json
current_status: outputs/right_conducting/tcn_alltest_latest/current_status_fulltest_latest.json
```

Key values:

```text
discovered raw CSV files: 15
scoreable processed sessions: 11
sample count at margin 3s: 1824
tempo accuracy: 1.0000
gain accuracy: 1.0000
false switches / min: 0.0000
missed switches: 0
runtime p90: 1.9984 ms
strict independent heldout: NO_GO, P0 0/8
overall goal status: IN_PROGRESS
```

## Presentation Updates

`presentation_training_summary.md` now references:

```text
latest TCN report: docs/exp/goal_reports/2026-06-17_117_full_test_release_and_status_rerun.md
handoff refresh report: docs/exp/goal_reports/2026-06-17_119_tcn_handoff_and_model_card_refresh.md
TCN score: outputs/right_conducting/tcn_alltest_latest/stream_set_score_fulltest_latest.json
TCN current status: outputs/right_conducting/tcn_alltest_latest/current_status_fulltest_latest.json
```

It also explicitly lists:

```text
discovered raw CSV files: 15
eval sessions: 11
```

## Verification

Stale reference search:

```text
No stale matches for:
  MotionBERT-Lite pretrained encoder를 사용한다
  stream_set_score.json
  latest TCN report: docs/exp/goal_reports/2026-06-17_106
  dataset/evaluation/session_20260616_222455
  MotionBERT representation에서
```

Document assertion:

```text
submission_presentation_latest_tcn_assertions_ok
```

## Current Status

This is a report/presentation alignment update. It does not change model weights or scores. The selected TCN live path remains `GO` on supplied fixed-camera data, and the full goal remains `IN_PROGRESS` until strict independent heldout roots are supplied and pass.
