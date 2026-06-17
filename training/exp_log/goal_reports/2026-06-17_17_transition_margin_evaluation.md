# Goal Report 17: Transition Margin Evaluation

## Purpose

The current eval session has real tempo changes while the performer is likely still moving between tempi.

Existing `stable_only` removes windows with `mixed_bpm_label=True`, but it does not remove stable-labeled windows immediately before or after a transition. This report re-scores the selected 60f live artifact after excluding windows around BPM transition times.

Primary question:

```text
Does margin filtering improve the model because transition windows were ambiguous,
or does the model still fail the stable 80 BPM tail after the 120 -> 80 transition?
```

## Evaluation Setup

Artifact:

```text
outputs/right_conducting/selected/feature_baseline_live_v0.json
```

Eval session:

```text
dataset/evaluation_transitions/session_20260616_222455_eval
```

Scoreable original eval files:

```text
labels_frame.jsonl
labels_window.jsonl
pose_right_h36m_masked.npy
right_rule_features.npy
```

Excluded eval-local augmentation artifacts:

```text
recommended_augmented_v0/
labels_tempo_augmented_15f.jsonl
tempo_augmented_15f.npy
```

Window:

```text
window_frames: 60
stride_frames: 3
fps: 14.985
input_norm: camera
feature_subset: all
```

Transition times from `manual_timeline.json`:

```text
22.0s: 100 -> 120 BPM
54.0s: 120 -> 80 BPM
```

Filtering rule:

```text
1. Exclude mixed_bpm_label=True windows.
2. Exclude any window whose [start_elapsed_seconds, end_elapsed_seconds]
   overlaps transition_time +/- transition_margin_seconds.
```

Replay metrics are reference-only because margin filtering shifts the apparent switch row.

## Command

```bash
python tools/evaluate_right_conducting_transition_margins.py \
  --artifact outputs/right_conducting/selected/feature_baseline_live_v0.json \
  --eval-session dataset/evaluation_transitions/session_20260616_222455_eval \
  --eval-window-frames 60 \
  --eval-stride-frames 3 \
  --input-norm camera \
  --margins 0,0.5,1,2,3 \
  --output-json outputs/right_conducting/transition_margin_scores_222455_60f.json \
  --output-md outputs/right_conducting/transition_margin_scores_222455_60f.md
```

Artifacts:

```text
outputs/right_conducting/transition_margin_scores_222455_60f.json
outputs/right_conducting/transition_margin_scores_222455_60f.md
```

## Offline Classification

| margin_s | sample_count | mixed_excluded | margin_excluded | tempo_acc | tempo_macro_f1 | 80_recall | 80_support | bpm_mae | gain_acc | dynamics_mae |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.0 | 243 | 38 | 0 | 0.5514 | 0.2885 | 0.0000 | 11 | 10.6173 | 0.7654 | 0.1407 |
| 0.5 | 231 | 38 | 12 | 0.5671 | 0.2943 | 0.0000 | 8 | 10.3896 | 0.7532 | 0.1481 |
| 1.0 | 223 | 38 | 20 | 0.5830 | 0.3013 | 0.0000 | 6 | 10.0448 | 0.7444 | 0.1534 |
| 2.0 | 203 | 38 | 40 | 0.6158 | 0.3174 | 0.0000 | 1 | 9.3596 | 0.7192 | 0.1685 |
| 3.0 | 187 | 38 | 56 | 0.6310 | 0.3255 | 0.0000 | 0 | 9.1979 | 0.6952 | 0.1829 |

True 80 BPM prediction counts:

| margin_s | true 80 support | predicted as 80 | predicted as 100 | predicted as 120 |
|---:|---:|---:|---:|---:|
| 0.0 | 11 | 0 | 8 | 3 |
| 0.5 | 8 | 0 | 5 | 3 |
| 1.0 | 6 | 0 | 4 | 2 |
| 2.0 | 1 | 0 | 1 | 0 |
| 3.0 | 0 | 0 | 0 | 0 |

## Streaming Replay Reference

| margin_s | row_count | raw_tempo_acc | raw_false_switches_per_min | raw_missed | smoothed_tempo_acc | smoothed_false_switches_per_min | smoothed_missed |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.0 | 243 | 0.5514 | 17.1243 | 1 | 0.6214 | 4.2811 | 1 |
| 0.5 | 231 | 0.5671 | 17.1243 | 1 | 0.6364 | 4.2811 | 1 |
| 1.0 | 223 | 0.5830 | 16.0540 | 1 | 0.6413 | 4.2811 | 1 |
| 2.0 | 203 | 0.6158 | 13.9135 | 1 | 0.6552 | 3.2108 | 1 |
| 3.0 | 187 | 0.6310 | 14.0258 | 0 | 0.6578 | 3.8252 | 0 |

## Interpretation

Margin filtering increases overall tempo accuracy:

```text
0.0s margin: 0.5514
3.0s margin: 0.6310
```

But this is not a real recovery of the down-transition problem.

Reason:

```text
80 BPM support shrinks from 11 -> 0 as the margin grows.
80 BPM recall remains 0.0000 for every margin where any 80 BPM window remains.
At margin 0.0, true 80 windows are predicted as {100: 8, 120: 3}.
At margin 1.0, true 80 windows are predicted as {100: 4, 120: 2}.
At margin 2.0, the only remaining true 80 window is predicted as 100.
```

Conclusion:

```text
The 120 -> 80 failure is not just transition-boundary ambiguity.
The current selected fallback cannot classify the stable 80 BPM tail in this eval session.
```

Deployment implication:

```text
Do not claim robust down-transition live control with the current selected artifact.
Use transition-margin score as a stricter diagnostic table, but keep classification metrics as the primary evidence.
Replay delay after margin filtering is only reference evidence.
```

## Decision

```text
selected 60f fallback: still acceptable only as a temporary live fallback.
robust 120 -> 80 live control: NO-GO.
next model step: improve raw classifier for the 80 BPM tail, not smoother-only tuning.
```
