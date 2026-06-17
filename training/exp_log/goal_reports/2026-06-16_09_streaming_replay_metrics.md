# Goal Report 09 - Streaming Replay Metrics

## Status

Current stage:

```text
stream replay metric functions: implemented
stream replay CLI: implemented
selected fallback artifact policy: tuned and re-exported
222455_eval 60f replay metrics: measured
```

Current decision:

```text
selected live fallback: feature_baseline_live_v0
selected policy: switch_threshold 0.15, fast_switch_threshold 0.40, confirm_updates 2
deep MotionBERT model: still not selected
```

## Why This Step

Report 08 exported the feature-baseline fallback artifact, but export score was a window classification score. Live behavior also needs temporal stability metrics:

```text
false switches per minute
prediction switch count
switch delay after true tempo change
effect of smoothing policy
```

This step replays the selected artifact across the evaluation timeline using 60-frame windows and stride 3.

## Code Change

Added:

```text
lib/right_conducting/stream_replay.py
tools/replay_right_conducting_stream.py
tests/test_stream_replay.py
tests/test_replay_right_conducting_stream_cli.py
```

Updated:

```text
tools/export_right_conducting_fallback.py
tests/test_export_right_conducting_fallback_cli.py
```

The export CLI now accepts policy overrides:

```text
--switch-threshold
--fast-switch-threshold
--confirm-updates
```

## Commands

Re-export tuned fallback:

```bash
python tools/export_right_conducting_fallback.py \
  --dataset-dir outputs/right_conducting/dataset_v0_60f \
  --zip dataset/recordings.zip \
  --score-json outputs/right_conducting/baseline_scores_v0_60f_eval60stable.json \
  --output-dir outputs/right_conducting/selected \
  --artifact-name feature_baseline_live_v0.json \
  --switch-threshold 0.15 \
  --fast-switch-threshold 0.40 \
  --confirm-updates 2
```

Replay:

```bash
python tools/replay_right_conducting_stream.py \
  --artifact outputs/right_conducting/selected/feature_baseline_live_v0.json \
  --eval-session dataset/evaluation_transitions/session_20260616_222455_eval \
  --eval-window-frames 60 \
  --eval-stride-frames 3 \
  --output-json outputs/right_conducting/stream_replay_222455_60f_tuned.json \
  --output-md outputs/right_conducting/stream_replay_222455_60f_tuned.md \
  --output-rows outputs/right_conducting/stream_replay_222455_60f_tuned_rows.jsonl
```

## Artifacts

```text
outputs/right_conducting/selected/feature_baseline_live_v0.json
outputs/right_conducting/selected/feature_baseline_live_v0_structure.md
outputs/right_conducting/selected/selected_model_manifest.json
outputs/right_conducting/stream_replay_222455_60f_tuned.json
outputs/right_conducting/stream_replay_222455_60f_tuned.md
outputs/right_conducting/stream_replay_222455_60f_tuned_rows.jsonl
```

## Policy

The original exported threshold `0.58` was too high for the centroid confidence scale:

```text
raw tempo confidence max: about 0.45
old switch_threshold: 0.58
effect: almost all tempo updates held
```

Tuned policy:

```text
bpm_ema_alpha: 0.15
dynamics_ema_alpha: 0.10
switch_threshold: 0.15
switch_margin: 0.12
confirm_updates: 2
fast_switch_threshold: 0.40
hold_on_low_confidence: true
max_hold_seconds: 2.0
```

## Replay Metrics

Evaluation:

```text
eval_session: dataset/evaluation_transitions/session_20260616_222455_eval
window_frames: 60
stride_frames: 3
row_count: 281
true tempo switches: 2
```

| mode | tempo_acc | gain_acc | pred_switch_count | false_switch_count | false_switches_per_min | switch_delay_mean_s | switch_delay_p90_s |
|---|---:|---:|---:|---:|---:|---:|---:|
| raw | 0.4982 | 0.7936 | 30 | 16 | 17.1243 | 6.6031 | 6.6031 |
| smoothed | 0.4698 | 0.8434 | 8 | 4 | 4.2811 | 7.6037 | 7.6037 |

## Interpretation

Smoothing improves stability but costs tempo accuracy:

```text
false switches/min: 17.1243 -> 4.2811
predicted switches: 30 -> 8
tempo_acc: 0.4982 -> 0.4698
gain_acc: 0.7936 -> 0.8434
switch delay mean: 6.6031s -> 7.6037s
```

The fallback is streamable, but not yet strong enough to claim robust conducting control. The current behavior is conservative: it reduces false tempo changes, but reacts late.

## Gate Check

Current live fallback gate:

```text
has exported parameter artifact: yes
has stream replay metrics: yes
false switches reduced by smoothing: yes
switch delay under 2 seconds: no
deep model beats fallback on heldout: no
```

Decision:

```text
Use feature_baseline_live_v0 only as fallback/demo baseline.
Do not claim final stable live tempo control yet.
```

## Next Step

The next useful step is to improve reaction speed without recovering the raw false-switch rate:

```text
1. tune confidence calibration instead of raw centroid confidence
2. add margin-aware switch logic using top-2 distance margin
3. evaluate stable vs mixed transition windows separately
4. relabel session_20260616_215630_eval for second transition replay
5. try temporal MotionBERT head if heldout data improves
```

Next report target:

```text
Goal Report 10 - Calibration and Second Eval Check
```
