# Goal Report 13 - Temporal Feature Classifier Probe

## Status

Current stage:

```text
temporal feature classifier: implemented and evaluated
30f c2/c3/c5 temporal ridge: no-go on heldout transition
final live model: not selected
```

Current decision:

```text
Do not use temporal_feature_ridge_v0_30f_c5 as the live model.
It improves within-subject CV over single-window 30f, but collapses on heldout transition.
```

## Why This Step

Report 12 showed:

```text
30f raw delay is better than 60f.
30f single-window predictions are unstable.
threshold-only smoothing creates pre-switch or missed-switch artifacts.
```

This step tests whether a causal temporal classifier over recent handcrafted features can keep the 30f latency advantage while improving stability.

## Model

Input:

```text
30f pose window
-> 16 handcrafted right-arm features
-> causal context concat over N windows
```

Classifier:

```text
Standardized ridge classifier
tempo head: 4-class 60/80/100/120
gain head: binary small/large
```

For `context_size = 5`:

```text
base feature dim: 16
temporal feature dim: 80
window duration: about 2s at current 15fps
history span: about 2.8s because stride is 3 frames ~= 0.2s
```

## Code Change

Added:

```text
lib/right_conducting/temporal_classifier.py
tools/evaluate_right_conducting_temporal.py
tools/replay_right_conducting_temporal.py
tools/sweep_right_conducting_temporal_policy.py
tests/test_temporal_classifier.py
tests/test_evaluate_temporal_cli.py
tests/test_replay_temporal_cli.py
tests/test_sweep_temporal_policy_cli.py
```

Artifact stores model structure and parameters:

```text
model_type
window_frames
stride_frames
context_size
base_feature_dim
tempo_model.classes / mean / std / weights
gain_model.classes / mean / std / weights
streaming policy
score_summary
```

## Commands

Main c5 evaluation:

```bash
python tools/evaluate_right_conducting_temporal.py \
  --dataset-dir outputs/right_conducting/dataset_v0_30f \
  --zip dataset/recordings.zip \
  --eval-session dataset/evaluation_transitions/session_20260616_222455_eval \
  --eval-window-frames 30 \
  --eval-stride-frames 3 \
  --eval-stable-only \
  --context-size 5 \
  --ridge-alpha 1.0 \
  --output-json outputs/right_conducting/temporal_scores_v0_30f_c5.json \
  --output-md outputs/right_conducting/temporal_scores_v0_30f_c5.md \
  --output-artifact outputs/right_conducting/temporal_30f_c5/temporal_feature_live_v0_30f_c5.json
```

Replay:

```bash
python tools/replay_right_conducting_temporal.py \
  --artifact outputs/right_conducting/temporal_30f_c5/temporal_feature_live_v0_30f_c5.json \
  --eval-session dataset/evaluation_transitions/session_20260616_222455_eval \
  --eval-window-frames 30 \
  --eval-stride-frames 3 \
  --context-size 5 \
  --switch-threshold 0.15 \
  --fast-switch-threshold 0.40 \
  --confirm-updates 2 \
  --output-json outputs/right_conducting/temporal_replay_222455_30f_c5_tuned.json \
  --output-md outputs/right_conducting/temporal_replay_222455_30f_c5_tuned.md \
  --output-rows outputs/right_conducting/temporal_replay_222455_30f_c5_tuned_rows.jsonl
```

## Artifacts

```text
outputs/right_conducting/temporal_scores_v0_30f_c2.json
outputs/right_conducting/temporal_scores_v0_30f_c3.json
outputs/right_conducting/temporal_scores_v0_30f_c5.json
outputs/right_conducting/temporal_30f_c5/temporal_feature_live_v0_30f_c5.json
outputs/right_conducting/temporal_replay_222455_30f_c5_tuned.json
outputs/right_conducting/temporal_replay_222455_30f_c5_tuned_analysis.json
outputs/right_conducting/temporal_policy_sweep_222455_30f_c5.json
```

## Heldout Score

| model | context | cv tempo_acc | heldout tempo_acc | bpm_mae | heldout gain_acc |
|---|---:|---:|---:|---:|---:|
| single-window feature baseline | 1 | 0.4757 | 0.4249 | 15.2381 | 0.7875 |
| temporal ridge | 2 | 0.5356 | 0.2601 | 15.8242 | 0.7582 |
| temporal ridge | 3 | 0.5354 | 0.2527 | 16.5568 | 0.7582 |
| temporal ridge | 5 | 0.5391 | 0.2491 | 16.3370 | 0.7546 |

Interpretation:

```text
Temporal ridge improves within-subject CV.
It hurts heldout transition tempo substantially.
This is another overfitting/generalization signal.
```

## Stream Replay

c5 tuned policy:

```text
switch_threshold: 0.15
fast_switch_threshold: 0.40
confirm_updates: 2
```

| mode | tempo_acc | false_switches_per_min | switch_delay_mean_s | switch_delay_p90_s |
|---|---:|---:|---:|---:|
| raw | 0.2509 | 20.6677 | 17.4088 | 27.6538 |
| smoothed | 0.2474 | 10.3338 | 30.4154 | 30.4154 |

Policy sweep selected under `false_switches_per_min <= 5`:

```text
switch_threshold: 0.35
fast_switch_threshold: 0.40
confirm_updates: 2
tempo_acc: 0.2405
false_switches_per_min: 1.0334
switch_delay_mean_s: 30.6154
```

This is not usable for live control because the low false-switch count is achieved by barely switching.

## Diagnosis

Heldout prediction distribution:

```text
true tempo classes:
  100 BPM class 2: 106 windows
  120 BPM class 3: 159 windows
  80 BPM class 1: 26 windows

temporal c5 raw predictions:
  class 2: 233 windows
  class 3: 42 windows
  class 0: 15 windows
  class 1: 1 window
```

The temporal ridge classifier sticks near class 2 and reaches the actual transition classes too late.

## Gate

Pass line:

```text
heldout tempo_acc >= current 30f baseline
false_switches_per_min <= 5
switch_delay_p90_s <= 3
raw_missed_switch_count = 0
```

Temporal ridge c5 status:

```text
heldout tempo_acc: fail
false_switches_per_min: fail for tuned, pass only with unusable high-delay sweep row
switch_delay_p90_s: fail
raw_missed_switch_count: pass, but too late
```

## Decision

```text
temporal_feature_ridge_v0_30f_c5: NO-GO
single-window 60f fallback remains the current selected live fallback
30f single-window remains a latency probe
```

## Next Step

The next step should move away from camera-coordinate handcrafted features:

```text
1. compare normalization modes on the same 30f/60f heldout transition
2. then retry temporal classifier only if normalization improves heldout alignment
3. relabel session_20260616_215630_eval before making stronger live claims
```
