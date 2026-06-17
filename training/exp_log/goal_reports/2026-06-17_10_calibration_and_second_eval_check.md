# Goal Report 10 - Calibration and Second Eval Check

## Status

Current stage:

```text
second eval session check: done
stream policy sweep CLI: implemented
policy sweep artifact: generated
selected artifact policy: consistent with sweep
```

Current decision:

```text
session_20260616_215630_eval: still excluded from transition scoring
selected live fallback policy: switch_threshold 0.15, fast_switch_threshold 0.40, confirm_updates 2
```

## Second Eval Check

Checked:

```text
dataset/evaluation_transitions/session_20260616_215630_eval
```

Current evidence:

```text
manual_timeline.json: missing
labels_frame.jsonl: 900 frames, all bpm_target = 100
labels_window.jsonl: 131 windows, all tempo_class = 2
pose_right_h36m_masked.npy: [900, 17, 3]
```

Decision:

```text
Do not use session_20260616_215630_eval for transition replay yet.
It still needs tempo transition relabeling.
```

## Code Change

Added reproducible policy sweep:

```text
tools/sweep_right_conducting_stream_policy.py
tests/test_sweep_stream_policy_cli.py
```

The sweep evaluates multiple stream policies and selects the highest tempo accuracy under a maximum false-switch constraint. If metrics tie, the selector prefers the more conservative `confirm_updates`.

## Sweep Command

```bash
python tools/sweep_right_conducting_stream_policy.py \
  --artifact outputs/right_conducting/selected/feature_baseline_live_v0.json \
  --eval-session dataset/evaluation_transitions/session_20260616_222455_eval \
  --eval-window-frames 60 \
  --eval-stride-frames 3 \
  --switch-thresholds 0.05,0.10,0.15,0.20,0.25 \
  --fast-switch-thresholds 0.40 \
  --confirm-updates 1,2 \
  --max-false-switches-per-min 5.0 \
  --output-json outputs/right_conducting/stream_policy_sweep_222455.json \
  --output-md outputs/right_conducting/stream_policy_sweep_222455.md
```

## Artifacts

```text
outputs/right_conducting/stream_policy_sweep_222455.json
outputs/right_conducting/stream_policy_sweep_222455.md
outputs/right_conducting/selected/feature_baseline_live_v0.json
outputs/right_conducting/selected/selected_model_manifest.json
```

## Selected Policy

Sweep constraint:

```text
max_false_switches_per_min: 5.0
```

Selected:

```text
switch_threshold: 0.15
fast_switch_threshold: 0.40
confirm_updates: 2
tempo_acc: 0.4698
gain_acc: 0.8434
pred_switch_count: 8
false_switch_count: 4
false_switches_per_min: 4.2811
switch_delay_mean_s: 7.6037
switch_delay_p90_s: 7.6037
```

This matches the currently exported selected fallback artifact.

## Policy Sweep Table

| switch_threshold | confirm_updates | tempo_acc | gain_acc | false_switches_per_min | switch_delay_mean_s | pred_switch_count |
|---:|---:|---:|---:|---:|---:|---:|
| 0.05 | 1 | 0.4626 | 0.8363 | 9.6324 | 6.8033 | 16 |
| 0.05 | 2 | 0.4626 | 0.8363 | 9.6324 | 6.8033 | 16 |
| 0.10 | 1 | 0.4306 | 0.8399 | 9.6324 | 7.0036 | 15 |
| 0.10 | 2 | 0.4306 | 0.8399 | 9.6324 | 7.0036 | 15 |
| 0.15 | 1 | 0.4698 | 0.8434 | 4.2811 | 7.6037 | 8 |
| 0.15 | 2 | 0.4698 | 0.8434 | 4.2811 | 7.6037 | 8 |
| 0.20 | 1 | 0.3559 | 0.9075 | 4.2811 | 14.6069 | 8 |
| 0.20 | 2 | 0.3559 | 0.9075 | 4.2811 | 14.6069 | 8 |
| 0.25 | 1 | 0.2954 | 0.9110 | 3.2108 | 14.6069 | 6 |
| 0.25 | 2 | 0.2954 | 0.9110 | 3.2108 | 14.6069 | 6 |

## Interpretation

The current confidence scale is not calibrated like a probability:

```text
raw centroid confidence max: about 0.45
original policy threshold 0.58: too high
```

Lowering the threshold restores switching, but there is still a stability/speed tradeoff:

```text
lower threshold: faster, more false switches
higher threshold: fewer false switches, much slower switch delay
selected threshold 0.15: best tempo_acc under 5 false switches/min
```

## Remaining Risk

The selected policy is justified for the current single transition session only.

```text
second transition eval is unavailable until 215630 is relabeled
switch delay is still too high for final live conducting
confidence calibration is heuristic, not learned
deep model still fails heldout tempo gate
```

## Next Step

Next report should reduce switch delay or add a valid second eval:

```text
1. relabel session_20260616_215630_eval and rerun replay
2. add calibrated confidence mapping from validation folds
3. test a faster policy with allowed false_switch budget if demo needs responsiveness
4. try temporal MotionBERT head after heldout labels improve
```

Next report target:

```text
Goal Report 11 - Second Eval Relabel or Confidence Calibration
```
