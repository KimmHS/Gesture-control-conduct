# Goal Report 08 - Live Fallback Export

## Status

Current stage:

```text
deep MotionBERT stats head heldout gate: failed
feature-baseline live fallback artifact: exported
model parameter JSON: exported
model structure file: exported
selected model manifest: exported
```

Current decision:

```text
selected live fallback for tempo: handcrafted_feature_ml
selected final deep model: not selected yet
```

## Why This Step

Report 07 showed that the MotionBERT stats head is not stable enough for transition/live tempo:

```text
feature_baseline transition_eval_222455_60f_stable tempo_acc: 0.5514
MotionBERT stats transition_eval_222455_60f_stable tempo_acc: 0.3128
```

The goal still needs an artifact that can be wired into a stream pipeline. This step exports the best current transition fallback so live integration has a concrete parameter file and structure file.

## Code Change

Added runtime/export support:

```text
lib/right_conducting/live_fallback.py
tools/export_right_conducting_fallback.py
tests/test_live_fallback.py
tests/test_export_right_conducting_fallback_cli.py
```

Runtime structure:

```text
pose window [60, 17, 3]
  -> 16 handcrafted right-arm motion features
  -> nearest-centroid tempo classifier
  -> nearest-centroid gain classifier
  -> confidence estimate from centroid distance margin
  -> LiveSmoother EMA + low-confidence hold + confirm switch
```

This is a fallback artifact, not the final deep MotionBERT model.

## Export Command

```bash
python tools/export_right_conducting_fallback.py \
  --dataset-dir outputs/right_conducting/dataset_v0_60f \
  --zip dataset/recordings.zip \
  --score-json outputs/right_conducting/baseline_scores_v0_60f_eval60stable.json \
  --output-dir outputs/right_conducting/selected \
  --artifact-name feature_baseline_live_v0.json
```

## Artifacts

```text
outputs/right_conducting/selected/feature_baseline_live_v0.json
outputs/right_conducting/selected/feature_baseline_live_v0_structure.md
outputs/right_conducting/selected/selected_model_manifest.json
```

Artifact summary:

```text
model_type: handcrafted_feature_ml
window_frames: 60
stride_frames: 3
feature_dim: 16
bpm_bins: [60, 80, 100, 120]
tempo_classes: [0, 1, 2, 3]
gain_classes: [0, 1]
```

Score embedded in artifact:

```text
eval_set: transition_eval_222455_60f_stable
tempo_acc: 0.5514
tempo_macro_f1: 0.2885
bpm_mae_window: 10.6173
gain_acc: 0.7654
gain_macro_f1: 0.5859
dynamics_mae_window: 0.1407
```

## Live Policy

Exported default policy:

```text
bpm_ema_alpha: 0.15
dynamics_ema_alpha: 0.10
switch_threshold: 0.58
switch_margin: 0.12
confirm_updates: 2
fast_switch_threshold: 0.78
hold_on_low_confidence: true
max_hold_seconds: 2.0
```

The smoother behavior is intentionally conservative:

```text
low confidence tempo prediction -> hold previous tempo
same new tempo for confirm_updates -> switch
very high confidence new tempo -> fast switch
```

## Gate Check

Live fallback gate:

```text
must produce a parameter artifact and structure file
must use the best current transition tempo model
must document that deep model is not selected yet
```

Result:

```text
PASS for fallback export
NO-GO for final deep model selection
```

## Remaining Risk

This artifact gives a streamable fallback, but it is not a strong generalization result:

```text
single-session transition heldout
imbalanced stable windows: 120 BPM = 141, 100 BPM = 91, 80 BPM = 11
small dynamics windows are scarce
cross-subject generalization not proven
```

## Next Step

Next report should either improve the deep model or turn this fallback into a replay benchmark:

```text
1. implement streaming replay metrics with LiveSmoother
2. report false switches per minute and switch delay on 60f stable/mixed windows
3. add session_20260616_215630_eval after relabel
4. try MotionBERT temporal head over [T, 3, 512]
```

Next report target:

```text
Goal Report 09 - Streaming Replay Metrics
```
