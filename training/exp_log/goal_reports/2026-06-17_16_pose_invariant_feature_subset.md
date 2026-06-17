# Goal Report 16: Pose-Invariant Feature Subset Candidate

## Purpose

Report 15 showed that the selected 60f camera fallback misses the `120 -> 80` transition because the raw classifier never emits class `1` in the stable 80 BPM tail.

This report tests a smaller handcrafted feature subset that removes static relative pose mean features.

Target change:

```text
drop/downweight:
  rel_wrist_x_mean
  rel_wrist_y_mean
  rel_elbow_x_mean
  rel_elbow_y_mean

keep:
  wrist speed / acceleration stats
  shoulder-wrist radius stats
  rel wrist x/y std
  right arm valid ratio
  dominant_bpm
```

Implementation:

```text
feature_subset: pose_invariant
source feature dim: 16
selected feature dim: 12
```

## Commands

60f stable heldout:

```bash
python tools/evaluate_right_conducting_baselines.py \
  --dataset-dir outputs/right_conducting/dataset_v0_60f \
  --zip dataset/recordings.zip \
  --eval-session dataset/evaluation_transitions/session_20260616_222455_eval \
  --eval-window-frames 60 \
  --eval-stride-frames 3 \
  --eval-stable-only \
  --input-norm camera \
  --feature-subset pose_invariant \
  --output-json outputs/right_conducting/pose_invariant_scores_v0_60f.json \
  --output-md outputs/right_conducting/pose_invariant_scores_v0_60f.md
```

30f stable heldout:

```bash
python tools/evaluate_right_conducting_baselines.py \
  --dataset-dir outputs/right_conducting/dataset_v0_30f \
  --zip dataset/recordings.zip \
  --eval-session dataset/evaluation_transitions/session_20260616_222455_eval \
  --eval-window-frames 30 \
  --eval-stride-frames 3 \
  --eval-stable-only \
  --input-norm camera \
  --feature-subset pose_invariant \
  --output-json outputs/right_conducting/pose_invariant_scores_v0_30f.json \
  --output-md outputs/right_conducting/pose_invariant_scores_v0_30f.md
```

Live replay artifacts:

```text
outputs/right_conducting/stream_replay_222455_60f_pose_invariant_tuned.json
outputs/right_conducting/stream_replay_222455_60f_pose_invariant_tuned_analysis.json
outputs/right_conducting/stream_replay_222455_30f_pose_invariant_tuned.json
outputs/right_conducting/stream_replay_222455_30f_pose_invariant_tuned_analysis.json
outputs/right_conducting/stream_policy_sweep_222455_60f_pose_invariant.json
outputs/right_conducting/stream_policy_sweep_222455_30f_pose_invariant.json
```

Summary artifact:

```text
outputs/right_conducting/pose_invariant_report16_summary.json
```

## Stable Heldout Score

Evaluation set:

```text
dataset/evaluation_transitions/session_20260616_222455_eval
stable-only regenerated windows from labels_frame.jsonl
eval-local augmentation artifacts excluded
```

| candidate | feature_subset | window | cv_mean tempo_acc | stable tempo_acc | stable bpm_mae | stable gain_acc |
|---|---|---:|---:|---:|---:|---:|
| 60f selected fallback | all | 60 | 0.5152 | 0.5514 | 10.6173 | 0.7654 |
| 60f pose-invariant | pose_invariant | 60 | 0.4795 | 0.4938 | 13.0864 | 0.8189 |
| 30f latency probe | all | 30 | 0.4757 | 0.4249 | 15.2381 | 0.7875 |
| 30f pose-invariant | pose_invariant | 30 | 0.4522 | 0.4579 | 14.7985 | 0.8095 |

Interpretation:

```text
60f pose-invariant fixes part of the transition failure, but stable tempo drops by 0.0576 from the selected 60f fallback.
This fails the Report 15 acceptance line: stable heldout tempo_acc should not drop by more than about 0.03.

30f pose-invariant improves stable tempo over 30f all-features, but still does not beat the selected 60f fallback.
```

## Streaming Replay

Tuned policy:

```text
switch_threshold: 0.15
fast_switch_threshold: 0.40
confirm_updates: 2
```

| candidate | mode | tempo_acc | gain_acc | false_switches_per_min | reached true switches | missed true switches | switch_delay_mean_s |
|---|---|---:|---:|---:|---:|---:|---:|
| 60f all | raw | 0.4982 | 0.7936 | 17.1243 | 1/2 | 1/2 | 6.6031 |
| 60f all | smoothed | 0.4698 | 0.8434 | 4.2811 | 1/2 | 1/2 | 7.6037 |
| 60f pose-invariant | raw | 0.4484 | 0.8399 | 14.9837 | 2/2 | 0/2 | 3.0016 |
| 60f pose-invariant | smoothed | 0.3203 | 0.8505 | 5.3513 | 1/2 | 1/2 | 7.6037 |
| 30f all | raw | 0.4192 | 0.8041 | 18.6009 | 1/2 | 1/2 | 1.4010 |
| 30f all | smoothed | 0.3574 | 0.8351 | 11.3672 | 1/2 | 1/2 | 7.4039 |
| 30f pose-invariant | raw | 0.4502 | 0.8179 | 29.9682 | 2/2 | 0/2 | 2.1012 |
| 30f pose-invariant | smoothed | 0.3677 | 0.8041 | 11.3672 | 1/2 | 1/2 | 5.6032 |

Switch detail:

```text
60f pose-invariant raw:
  100 -> 120 delay: 2.2010s
  120 -> 80 delay: 3.8021s

30f pose-invariant raw:
  100 -> 120 delay: 1.4010s
  120 -> 80 delay: 2.8014s
```

Interpretation:

```text
Removing static pose means lets the raw classifier reach both true tempo switches.
The smoother still misses the final 80 BPM segment because the candidate is too unstable and the stable 80 tail is short.
```

## Policy Sweep

Constraint:

```text
false_switches_per_min <= 5.0
```

| candidate | switch_threshold | fast_switch_threshold | confirm_updates | tempo_acc | gain_acc | false_switches_per_min | switch_delay_mean_s |
|---|---:|---:|---:|---:|---:|---:|---:|
| 60f pose-invariant sweep | 0.20 | 0.50 | 3 | 0.3274 | 0.8541 | 4.2811 | 17.0084 |
| 30f pose-invariant sweep | 0.30 | 0.50 | 3 | 0.2199 | 0.8282 | 4.1335 | 18.0092 |

Interpretation:

```text
The sweep can suppress false switches below 5/min, but the delay becomes too large and tempo accuracy collapses.
This is not an acceptable live-control tradeoff.
```

## Decision

```text
pose_invariant feature subset: NO-GO as selected live model.
```

Reason:

```text
It fixes the raw missed 120 -> 80 switch, but stable heldout tempo accuracy falls below the acceptance line.
The live smoother either remains too noisy or becomes too slow when policy thresholds are tightened.
```

Keep selected fallback:

```text
outputs/right_conducting/selected/feature_baseline_live_v0.json
feature_subset: all
window: 60 frames
input_norm: camera
```

Keep pose-invariant artifacts as diagnostics:

```text
outputs/right_conducting/selected_60f_pose_invariant/feature_baseline_live_v0_60f_pose_invariant.json
outputs/right_conducting/selected_30f_pose_invariant/feature_baseline_live_v0_30f_pose_invariant.json
```

## Next Step

Do not continue with smoothing-only tuning.

Next candidate should combine both signals:

```text
hybrid feature classifier:
  keep static pose means, but downweight them
  keep motion-only features from pose_invariant
  add class-balanced or transition-weighted training
  prefer ridge/logistic model over pure nearest-centroid if needed
```

Gate for the next candidate:

```text
stable tempo_acc >= 0.52 on transition_eval_222455_60f_stable
raw reached true switches: 2/2
smoothed false_switches_per_min <= 5
smoothed missed true switches: 0/2
```
