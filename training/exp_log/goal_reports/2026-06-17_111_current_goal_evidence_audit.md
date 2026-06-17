# Report 111 - Current Goal Evidence Audit

## Purpose

This report freezes the current evidence after the final TCN all-test rerun and full unittest pass. It separates what is already usable for the fixed-camera live stream path from what is still missing before the full goal can be marked complete.

## Current Verdict

```text
overall goal: IN_PROGRESS
selected live model: TCN handmark live classifier
bundle: outputs/right_conducting/selected_tcn_handmark_live45f
live runtime: GO
release validation: GO
strict independent heldout: NO_GO
reason: dataset/strict_heldout_static_v1 and dataset/strict_heldout_transitions_v1 are absent
```

Do not close the goal as complete yet. The current model is live-ready for the supplied fixed-camera scope, but strict heldout generalization is not proven.

## Selected Model Evidence

```text
bundle_name: selected_tcn_handmark_live45f
manifest_model_name: tcn_right_conducting_live
model_type: causal_tcn_right_arm_pose
checkpoint: outputs/right_conducting/selected_tcn_handmark_live45f/tcn_conducting_head.pt
manifest: outputs/right_conducting/selected_tcn_handmark_live45f/tcn_conducting_live_manifest.json
structure: outputs/right_conducting/selected_tcn_handmark_live45f/tcn_conducting_live_structure.md
model_card: docs/exp/right_hand_conducting_model_card.md
trainable_parameters: 147910
```

Runtime structure:

```text
input: raw handmark CSV/stdin
pose window: [B, 45, 17, 3]
runtime tensor: [B, 9, 45]
fps: 15.0
stride_frames: 3
update interval: about 0.2s
cold start: about 3.0s
right_arm_indices: [14, 15, 16]
tempo bins: [60, 80, 100, 120]
gain classes: small, large
```

## Latest Score Evidence

Artifacts:

```text
outputs/right_conducting/tcn_alltest_latest/stream_set_score.json
outputs/right_conducting/tcn_alltest_latest/stream_set_gate.json
outputs/right_conducting/tcn_alltest_latest/stream_readiness.json
outputs/right_conducting/tcn_alltest_latest/stream_benchmark.json
outputs/right_conducting/tcn_alltest_latest/current_status_runner_snapshot.json
```

Scope:

```text
csv roots: dataset/static_variants_80, dataset/transitions
csv_count: 11
eval_session_count: 11
beat4: excluded
stable_only: true
margin used for selected gate: 3.0s
```

Margin 3s selected metrics:

```text
sample_count: 1824
mixed_bpm_excluded_count: 204
transition_margin_excluded_count: 423
tempo_acc: 1.0000
gain_acc: 1.0000
tempo_80_recall: 1.0000
tempo_100_recall: 1.0000
tempo_120_recall: 1.0000
tempo_support_by_class: 80=1152, 100=191, 120=481
bpm_mae_window: 0.0000
false_switches_per_min: 0.0000
missed_switch_count: 0
switch_delay_p90_s: 0.0000
```

Runtime evidence:

```text
readiness_status: GO
benchmark_p90_ms: 1.9984
benchmark_headroom_ratio: 100.0821
stream_rows: 216
stdin_rows: 3
output_contract_errors: 0
```

## Requirement Audit

| Requirement from goal | Current evidence | Status |
|---|---|---|
| Prompt analysis and survey first | `goal_reports/2026-06-16_01_prompt_analysis_and_augmentation_survey.md` | DONE |
| Data augmentation expansion explored | Reports 21, 25, 26; train-only augmentation policy and label-changing tempo/gain augmentation diagnostics | DONE for method exploration |
| Train and evaluate models | MotionBERT reports 47/59; TCN reports 79/80/83/106 | DONE for current supplied scope |
| Use available GPU sweep where useful | 5-GPU MotionBERT sweep reports 47/59; TCN window sweep reports 79/80 | DONE for available experiment set |
| Final stream environment can receive handmark data | `tools/run_tcn_handmark_csv_stream.py`, CSV/stdin runtime, Reports 87/88/90 | DONE for fixed-camera handmark CSV/stdin |
| Stable tempo/gain classification output | Latest TCN supplied-set gate GO with tempo/gain 1.0000 and false switches 0 | DONE for supplied fixed-camera set |
| Score table and model report | `right_hand_conducting_scores.md`, `right_hand_conducting_model_card.md`, Report 110 | DONE |
| Reproducible goal command surface | `tools/run_right_conducting_goal.py`, `scripts/run_tcn_strict_post_arrival_goal.sh` | DONE |
| Strict independent heldout proof | Missing roots and P0 coverage 0/8 | NOT DONE |

## Current Blocker

Strict roots are still missing:

```text
dataset/strict_heldout_static_v1
dataset/strict_heldout_transitions_v1
```

Required P0 strict coverage:

```text
static 80 BPM:
  2-beat large
  2-beat small
  3-beat large
  3-beat small

transition 120 -> 80 -> 120:
  2-beat large
  2-beat small
  3-beat large
  3-beat small
```

Current strict summary:

```text
strict_heldout_status: NO_GO
P0 required / present / missing: 8 / 0 / 8
blocker: missing strict heldout roots or required P0 coverage
```

## Completion Line

After strict data arrives, run:

```bash
scripts/run_tcn_strict_post_arrival_goal.sh
```

The goal can only be considered complete when that chain finishes with:

```text
tcn-release-validate: GO
heldout-independence: GO
strict-heldout-scope: GO
strict-heldout-preflight: GO
tcn-handmark-csv-set-gate: GO
tcn-handmark-stream-readiness: GO
tcn-goal-status: COMPLETE
tcn-current-status: strict_heldout_status GO
```

## Verification

Current assertion:

```text
selected_tcn_doc_and_artifact_assertions_ok
margin3_sample_count: 1824
tempo_acc: 1.0000
gain_acc: 1.0000
live_status: GO
strict_heldout_status: NO_GO
```

Full regression:

```text
PYTHONPATH=. python -m unittest discover tests -v
Ran 270 tests in 58.982s
OK
```
