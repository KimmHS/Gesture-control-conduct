# Goal Report 14: Normalization Comparison

## Purpose

This step checks whether camera-coordinate input is the bottleneck for live tempo/gain classification.

Current v0 scope:

```text
fps: about 15
tempo bins: 60 / 80 / 100 / 120
60 frames ~= 4s
30 frames ~= 2s latency probe
eval: dataset/evaluation_transitions/session_20260616_222455_eval
excluded eval: session_20260616_215630_eval until transition relabel
```

Normalization modes compared:

```text
camera
right_shoulder
right_arm_length
```

## Stable Heldout Score

These rows use original eval artifacts only. Eval-local augmented files are excluded.

| candidate | input_norm | tempo_acc | bpm_mae_window | gain_acc | dynamics_mae_window |
|---|---|---:|---:|---:|---:|
| 60f camera | camera | 0.5514 | 10.6173 | 0.7654 | 0.1407 |
| 60f right_shoulder | right_shoulder | 0.5473 | 10.7819 | 0.8066 | 0.1160 |
| 60f right_arm_length | right_arm_length | 0.4609 | 15.3086 | 0.5556 | 0.2667 |
| 30f camera | camera | 0.4249 | 15.2381 | 0.7875 | 0.1275 |
| 30f right_shoulder | right_shoulder | 0.4542 | 14.5055 | 0.8059 | 0.1165 |
| 30f right_arm_length | right_arm_length | 0.3663 | 18.0952 | 0.5275 | 0.2835 |

Interpretation:

```text
right_shoulder improves 30f tempo and gain.
right_shoulder improves 60f gain, but 60f camera is still slightly better for tempo.
right_arm_length hurts both tempo and gain, so it is no-go.
```

## Live Replay

Policy for tuned rows:

```text
switch_threshold: 0.15
fast_switch_threshold: 0.40
confirm_updates: 2
```

| candidate | mode | tempo_acc | gain_acc | false_switches_per_min | switch_delay_mean_s | missed_switches |
|---|---|---:|---:|---:|---:|---:|
| 60f camera | raw | 0.4982 | 0.7936 | 17.1243 | 6.6031 | 1 |
| 60f camera | smoothed | 0.4698 | 0.8434 | 4.2811 | 7.6037 | 1 |
| 60f right_shoulder | raw | 0.4947 | 0.8256 | 13.9135 | 6.6031 | 1 |
| 60f right_shoulder | smoothed | 0.4840 | 0.8470 | 4.2811 | 7.6037 | 1 |
| 30f camera | raw | 0.4192 | 0.7973 | 18.6009 | 1.4010 | 1 |
| 30f camera | smoothed | 0.3574 | 0.8179 | 11.3672 | 7.4039 | 1 |
| 30f right_shoulder | raw | 0.4467 | 0.8076 | 19.6343 | 1.4010 | 1 |
| 30f right_shoulder | smoothed | 0.3780 | 0.8316 | 11.3672 | 7.6040 | 1 |

Switch breakdown:

```text
60f camera:
  100 -> 120 reached, smoothed delay 7.6037s
  120 -> 80 missed

60f right_shoulder:
  100 -> 120 reached, smoothed delay 7.6037s
  120 -> 80 missed

30f camera:
  100 -> 120 reached, raw delay 1.4010s
  120 -> 80 missed

30f right_shoulder:
  100 -> 120 reached, raw delay 1.4010s
  120 -> 80 missed
```

## Policy Sweep Caveat

The right_shoulder policy sweep can select rows with `switch_delay_mean_s = 0.0000`, but replay analysis shows this is not a clean fast switch.

Sweep-selected right_shoulder policies:

| candidate | switch_threshold | fast_switch_threshold | confirm_updates | smoothed tempo_acc | smoothed gain_acc | false_switches_per_min | reported delay |
|---|---:|---:|---:|---:|---:|---:|---:|
| 30f right_shoulder | 0.30 | 0.50 | 3 | 0.5086 | 0.9966 | 4.1335 | 0.0000 |
| 60f right_shoulder | 0.30 | 0.50 | 3 | 0.6335 | 0.9893 | 2.1405 | 0.0000 |

Breakdown:

```text
100 -> 120:
  smoothed output is already target before the true switch.

120 -> 80:
  raw and smoothed output do not reach the target.
```

Conclusion:

```text
The 0.0000s delay is a pre-switch artifact.
Do not promote the sweep-selected right_shoulder policy as live success.
```

## Decision

Current selected fallback remains:

```text
outputs/right_conducting/selected/feature_baseline_live_v0.json
window_frames: 60
input_norm: camera
policy: switch_threshold 0.15, fast_switch_threshold 0.40, confirm_updates 2
```

Why:

```text
60f camera still has the best stable heldout tempo score.
60f right_shoulder improves gain and slightly improves smoothed replay tempo, but it still misses 120 -> 80.
30f right_shoulder improves 30f stable score, but live false switches remain too high.
right_arm_length is no-go.
```

Gate:

```text
GO for keeping right_shoulder as a future ablation/input_norm option.
NO-GO for replacing the selected live fallback.
NO-GO for right_arm_length.
```

## Artifacts

```text
outputs/right_conducting/normalization_scores_v0_60f_right_shoulder.json
outputs/right_conducting/normalization_scores_v0_60f_right_arm_length.json
outputs/right_conducting/normalization_scores_v0_30f_right_shoulder.json
outputs/right_conducting/normalization_scores_v0_30f_right_arm_length.json
outputs/right_conducting/selected_30f_right_shoulder/feature_baseline_live_v0_30f_right_shoulder.json
outputs/right_conducting/selected_60f_right_shoulder/feature_baseline_live_v0_60f_right_shoulder.json
outputs/right_conducting/stream_replay_222455_30f_right_shoulder_tuned.json
outputs/right_conducting/stream_replay_222455_30f_right_shoulder_tuned_analysis.json
outputs/right_conducting/stream_replay_222455_60f_right_shoulder_tuned.json
outputs/right_conducting/stream_replay_222455_60f_right_shoulder_tuned_analysis.json
outputs/right_conducting/stream_policy_sweep_222455_30f_right_shoulder.json
outputs/right_conducting/stream_policy_sweep_222455_60f_right_shoulder.json
```

## Commands

```bash
python tools/evaluate_right_conducting_baselines.py \
  --dataset-dir outputs/right_conducting/dataset_v0_60f \
  --zip dataset/recordings.zip \
  --eval-session dataset/evaluation_transitions/session_20260616_222455_eval \
  --eval-window-frames 60 \
  --eval-stride-frames 3 \
  --input-norm right_shoulder \
  --output-json outputs/right_conducting/normalization_scores_v0_60f_right_shoulder.json \
  --output-md outputs/right_conducting/normalization_scores_v0_60f_right_shoulder.md

python tools/replay_right_conducting_stream.py \
  --artifact outputs/right_conducting/selected_60f_right_shoulder/feature_baseline_live_v0_60f_right_shoulder.json \
  --eval-session dataset/evaluation_transitions/session_20260616_222455_eval \
  --eval-window-frames 60 \
  --eval-stride-frames 3 \
  --switch-threshold 0.15 \
  --fast-switch-threshold 0.40 \
  --confirm-updates 2 \
  --output-json outputs/right_conducting/stream_replay_222455_60f_right_shoulder_tuned.json \
  --output-md outputs/right_conducting/stream_replay_222455_60f_right_shoulder_tuned.md \
  --output-rows outputs/right_conducting/stream_replay_222455_60f_right_shoulder_tuned_rows.jsonl
```

## Next Step

Next movement should target the missed `120 -> 80` switch at the classifier level.

Priority:

```text
1. inspect examples around the missed 120 -> 80 segment
2. add transition-focused training windows or explicit down-transition eval labels
3. test a smaller model with class-balanced / transition-aware weighting
4. only then tune smoother again
```
