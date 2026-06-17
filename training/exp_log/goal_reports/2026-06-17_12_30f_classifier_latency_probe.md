# Goal Report 12 - 30f Classifier Latency Probe

## Status

Current stage:

```text
classifier-side latency probe: done
30-frame fallback candidate: evaluated
final live model: not selected
```

Current decision:

```text
30f windows reduce raw switch delay, but they do not solve stable live control.
30f is a useful latency probe, not the final selected artifact.
```

## Why This Step

Goal Report 11 showed that 60f live delay was mostly classifier-side:

```text
60f raw delay on 100 -> 120 BPM: 6.6031s
60f smoothed delay: 7.6037s
60f raw missed 120 -> 80 BPM
```

The next direct test is reducing the classifier input window:

```text
60 frames ~= 4s at current 15fps
30 frames ~= 2s at current 15fps
```

## Code Change

Small metadata/generalization fix:

```text
lib/right_conducting/dataset_prep.py
  windows_jsonl_name(window_frames)
  manifest.windows_file
  dataset_version right_conducting_v0_{window}f

tools/evaluate_right_conducting_baselines.py
  reads manifest.windows_file
  reports run_name/window_frames from manifest

tools/export_right_conducting_fallback.py
  reads manifest.windows_file
  exports dynamic pose window shape in structure report
  score_summary accepts matching stable transition rows, including 30f
```

This prevents 30f artifacts from being mislabeled as 60f.

## Commands

Dataset:

```bash
python tools/prepare_right_conducting_dataset.py \
  --zip dataset/recordings.zip \
  --output-dir outputs/right_conducting/dataset_v0_30f \
  --window-frames 30 \
  --stride-frames 3 \
  --folds 3 \
  --augment-copies 5 \
  --seed 42
```

Baseline score:

```bash
python tools/evaluate_right_conducting_baselines.py \
  --dataset-dir outputs/right_conducting/dataset_v0_30f \
  --zip dataset/recordings.zip \
  --eval-session dataset/evaluation_transitions/session_20260616_222455_eval \
  --eval-window-frames 30 \
  --eval-stride-frames 3 \
  --eval-stable-only \
  --output-json outputs/right_conducting/baseline_scores_v0_30f_eval30stable.json \
  --output-md outputs/right_conducting/baseline_scores_v0_30f_eval30stable.md
```

Replay and sweep:

```bash
python tools/replay_right_conducting_stream.py \
  --artifact outputs/right_conducting/selected_30f/feature_baseline_live_v0_30f.json \
  --eval-session dataset/evaluation_transitions/session_20260616_222455_eval \
  --eval-window-frames 30 \
  --eval-stride-frames 3 \
  --switch-threshold 0.15 \
  --fast-switch-threshold 0.40 \
  --confirm-updates 2 \
  --output-json outputs/right_conducting/stream_replay_222455_30f_tuned.json \
  --output-md outputs/right_conducting/stream_replay_222455_30f_tuned.md \
  --output-rows outputs/right_conducting/stream_replay_222455_30f_tuned_rows.jsonl

python tools/sweep_right_conducting_stream_policy.py \
  --artifact outputs/right_conducting/selected_30f/feature_baseline_live_v0_30f.json \
  --eval-session dataset/evaluation_transitions/session_20260616_222455_eval \
  --eval-window-frames 30 \
  --eval-stride-frames 3 \
  --switch-thresholds 0.05,0.10,0.15,0.20,0.25,0.30,0.35 \
  --fast-switch-thresholds 0.30,0.40,0.50 \
  --confirm-updates 1,2,3 \
  --max-false-switches-per-min 5.0 \
  --output-json outputs/right_conducting/stream_policy_sweep_222455_30f.json \
  --output-md outputs/right_conducting/stream_policy_sweep_222455_30f.md
```

## Artifacts

```text
outputs/right_conducting/dataset_v0_30f/
outputs/right_conducting/baseline_scores_v0_30f_eval30stable.json
outputs/right_conducting/baseline_scores_v0_30f_eval30stable.md
outputs/right_conducting/selected_30f/feature_baseline_live_v0_30f.json
outputs/right_conducting/selected_30f_sweep/feature_baseline_live_v0_30f_sweep.json
outputs/right_conducting/stream_replay_222455_30f_tuned.json
outputs/right_conducting/stream_replay_222455_30f_tuned_analysis.json
outputs/right_conducting/stream_policy_sweep_222455_30f.json
outputs/right_conducting/stream_replay_222455_30f_selected.json
outputs/right_conducting/stream_replay_222455_30f_selected_analysis.json
```

## Dataset Check

```text
take_count: 24
window_count: 8246
fold_count: 3
train augmentation ratio: 5.0x
validation augmentation: 0
windows_file: windows_30f_v0.jsonl
```

## 60f vs 30f Stable Heldout

| candidate | eval_set | tempo_acc | bpm_mae | gain_acc | dynamics_mae |
|---|---|---:|---:|---:|---:|
| 60f fallback | transition_eval_222455_60f_stable | 0.5514 | 10.6173 | 0.7654 | 0.1407 |
| 30f fallback | transition_eval_222455_30f_stable | 0.4249 | 15.2381 | 0.7875 | 0.1275 |

30f improves gain slightly, but hurts tempo classification on the stable heldout score.

## Replay Comparison

| candidate | mode | tempo_acc | false_switches_per_min | switch_delay_mean_s | raw_missed_switches |
|---|---|---:|---:|---:|---:|
| 60f tuned | raw | 0.4982 | 17.1243 | 6.6031 | 1 |
| 60f tuned | smoothed | 0.4698 | 4.2811 | 7.6037 | 1 |
| 30f tuned | raw | 0.4192 | 18.6009 | 1.4010 | 1 |
| 30f tuned | smoothed | 0.3574 | 11.3672 | 7.4039 | 1 |

Interpretation:

```text
30f raw delay is much better.
30f raw stability is worse.
The same smoothing policy over-holds 30f predictions and still misses the 80 BPM switch.
```

## 30f Policy Sweep

Sweep-selected row under `false_switches_per_min <= 5`:

```text
switch_threshold: 0.35
fast_switch_threshold: 0.50
confirm_updates: 3
tempo_acc: 0.4914
gain_acc: 0.9966
false_switches_per_min: 3.1002
switch_delay_mean_s: 0.0000
```

Important caveat:

```text
The 0.0000s delay is not a clean fast switch.
For 100 -> 120 BPM, smoothed output was already 120 BPM before the true switch.
This is an early false switch / pre-switch artifact.
```

Delay breakdown:

| transition | raw_delay_s | smoothed_delay_s | smoothed_target_before_switch | raw_missed |
|---|---:|---:|---|---|
| 100 -> 120 BPM | 1.4010 | 0.0000 | true | false |
| 120 -> 80 BPM | NA | NA | false | true |

## Gate

Current live pass line:

```text
false_switches_per_min <= 5
switch_delay_p90_s <= 3
raw_missed_switch_count = 0
no pre-switch on true transition
```

30f selected sweep status:

```text
false_switches_per_min: pass
reported switch_delay_p90_s: pass
raw_missed_switch_count: fail
pre-switch: fail
stable heldout tempo_acc: worse than 60f
```

## Decision

```text
Do not replace the current 60f fallback with 30f.
Keep 30f as evidence that shorter windows can reduce raw latency.
Next improvement must combine short-window responsiveness with stronger temporal/state modeling.
```

## Next Step

The next model-side step should not be another threshold-only sweep.

Recommended next work:

```text
1. train a temporal classifier over consecutive 30f/60f feature vectors
2. add transition-aware labels so early/pre-switch errors are penalized
3. compare normalization modes on 30f and 60f
4. rerun once session_20260616_215630_eval is relabeled
```
