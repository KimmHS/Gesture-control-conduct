# Transition Dataset Update Midreport

## Scope

This report summarizes the update after adding:

```text
dataset/transitions
```

No model retraining or additional scoring run was completed after this intake check.

## Current Dataset State

Existing stable training data remains scoreable:

```text
train_ready_count: 24
```

The current evaluation transition root contains one restored session:

```text
dataset/evaluation_transitions/session_20260616_215630_bpm100_beat4_large
```

It is still not scoreable as a transition eval set because it is pending relabel / timeline clarification.

## Newly Added Transition Sessions

`dataset/transitions` contains 11 sessions, about 301 MB total.

Summary:

| sequence | sessions |
|---|---:|
| 120 -> 80 -> 120 | 7 |
| 100 -> 80 -> 100 | 4 |

By dynamics prompt from `meta.json`:

| dynamics | sessions |
|---|---:|
| large | 6 |
| small | 5 |

By meter:

| meter | sessions |
|---:|---:|
| 2 | 3 |
| 3 | 4 |
| 4 | 4 |

The BPM changes occur around 15 s and 30 s in every session.

## Intake Decision

The current intake audit classifies all 11 new transition sessions as:

```text
train_review
```

Reason:

```text
train take should have one stable BPM target
```

This is correct. These sessions are not stable single-BPM training takes. They should not be silently mixed into the existing stable training zip.

Generated audit artifacts:

```text
outputs/right_conducting/dataset_intake_transitions_added.json
outputs/right_conducting/dataset_intake_transitions_added.md
```

## Current Selected Model

Current selected live artifact remains:

```text
outputs/right_conducting/selected/feature_baseline_live_v0.json
```

Its heldout transition score on the old `222455` stable-window eval is:

| metric | value |
|---|---:|
| tempo_acc | 0.5514 |
| tempo_macro_f1 | 0.2885 |
| bpm_mae_window | 10.6173 |
| gain_acc | 0.7654 |
| gain_macro_f1 | 0.5859 |
| dynamics_mae_window | 0.1407 |
| dynamics_corr | 0.2783 |

Gain is not stable enough to call solved. Accuracy is inflated by class imbalance:

| gain class | F1 | support |
|---|---:|---:|
| small | 0.3133 | 19 |
| large | 0.8586 | 224 |

## Important Label Finding

The new `dataset/transitions` labels contain continuous `dynamics` values, not explicit `small` / `large` class labels in the frame/window labels.

Observed window-level dynamics ranges:

| prompt | observed mean range |
|---|---|
| large | about 0.36 - 0.43 |
| small | about 0.12 - 0.18 |

A fixed `0.5` threshold would mark all new sessions as `small`. Therefore gain evaluation/training on this dataset needs calibration or class mapping before use.

## Main Gaps

1. No new transition dataset is scoreable yet under the current heldout-transition eval path.
2. The old scoreable eval session `session_20260616_222455_eval` is no longer present under `dataset/evaluation_transitions`.
3. The restored `215630` eval session has only one BPM target and still needs timeline/relabel work.
4. The new transition sessions have usable BPM changes, but they need a transition-aware intake path or manual/derived timeline metadata.
5. Gain still needs better balanced evaluation, especially for `small`.

## Recommended Next Step

Use `dataset/transitions` as transition-specific data, not stable train data.

Immediate path:

1. Build a transition manifest from label-derived change frames.
2. Add a transition eval path that can use label-derived BPM changes when `manual_timeline.json` is absent.
3. Apply margin-based stable-window scoring on the 11 new sessions.
4. For gain, calibrate small/large class mapping from per-session `meta.json` and observed `dynamics` distribution instead of using a fixed 0.5 threshold.
5. Re-run score table by margin: `0.0`, `0.5`, `1.0`, `2.0`, `3.0`.

