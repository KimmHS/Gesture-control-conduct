# Augmentation, Normalization, Delay, Smoothing Summary

Recommended short-window setting: `24f / 1.6s`, stride `3f / 0.2s`, transition boundary margin `+/-0.5s`.

## Data Augmentation / Normalization

### MotionBERT

- Dataset prep generated `5` augmentation candidates per train window, but the current MotionBERT head run effectively trained on original cached windows only.
- Evidence: `fold_augmented_counts={'fold_0': 0, 'fold_1': 0, 'fold_2': 0}`, `all_train_augmented_count=0`.
- Prepared augmentation policy: `augment_copies_per_train_window=5`, validation/eval samples are original only.
- Prepared augmentation recipes: coordinate jitter (`sigma=0.008`), confidence dropout (`max_len_frames=5`), small affine (`scale=1.03`, `rotation=3deg`), temporal stretch (`0.95/1.05` with BPM label adjusted), amplitude scaling (`large x0.85`, `small x1.15` with dynamics/gain label adjusted).
- Boundary handling: windows overlapping BPM transition `+/-0.5s` were dropped from training; for 24f this removed `182` windows and kept `10640` original windows.
- MotionBERT input normalization: `camera`; input mask mode `as_is`.
- Cached feature mode: `mean_std_delta`. It pools right-arm MotionBERT representations as mean, std, abs(delta) mean, abs(delta) std. Feature shape is `[10640, 2048]`.
- Head model also applies `LayerNorm` before the MLP head.

### TCN

- TCN quick-probe did not use synthetic augmentation; it trained on selected original windows only.
- 24f train filtering: source `2528`, selected `2346`, mixed-BPM excluded `106`, boundary excluded `76`.
- TCN normalization: input windows are normalized with train-set mean/std computed over batch and time for each input channel, then saved in the checkpoint as `input_mean` and `input_std`.
- TCN input is right shoulder/elbow/wrist x/y/confidence flattened to `[B, 9, T]`.

## Real-Time Delay

- Runtime policy is trailing-window only: no future frames are used.
- For `24f`, the model needs a `1.6s` input window before emitting a prediction for the window end timestamp.
- Update interval is `3f`, about `0.2s` at 15 fps.
- Smoothing policy uses `switch_threshold=0.58`, `fast_switch_threshold=0.78`, `confirm_updates=2`, BPM EMA `alpha=0.15`, dynamics EMA `alpha=0.10`.
- Practical interpretation: structural latency is dominated by the 1.6s trailing window; after a candidate switch appears, smoothing usually adds about one update step (~0.2s) unless confidence is high enough for fast switch.
- The observed replay delay below is measured from label switch time to first matching predicted switch timestamp in the evaluation rows.

| model | raw delay mean | raw delay p90 | smoothed delay mean | smoothed delay p90 | missed switches |
|---|---:|---:|---:|---:|---:|
| MotionBERT 24f | 0.096s | 0.330s | 0.271s | 0.736s | 0 |
| TCN quick-probe 24f | 0.000s | 0.000s | 0.000s | 0.000s | 0 |

## Smoothing: Before vs After

- Purpose: suppress temporary class flips near transition boundaries, where the raw model can oscillate.
- It does not change the training labels; it only stabilizes live/replay output after prediction.

| model | tempo raw | tempo smoothed | gain raw | gain smoothed | pred switches raw | pred switches smoothed | false/min raw | false/min smoothed | improvement |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| MotionBERT 24f | 0.8947 | 0.9339 | 0.9985 | 0.9993 | 199 | 73 | 19.69 | 5.98 | 69.6% lower false/min |
| TCN quick-probe 24f | 0.9996 | 1.0000 | 1.0000 | 1.0000 | 18 | 16 | 1.35 | 0.00 | 100.0% lower false/min |

## Talking Points

- Boundary policy: because human switch timing and label boundaries can easily be off by around 1s total, train/eval ignores transition +/-0.5s.
- Window policy: 2s felt too long, so the practical short-window candidate is `24f / 1.6s`; shorter windows were noisier around switching.
- Gain is not the bottleneck on the devset: MotionBERT 24f gain is `0.9985`, TCN 24f gain is `1.0000`. The harder part is tempo stability around transitions.
- Smoothing materially reduces switching noise. For MotionBERT 24f, false/min drops from `19.69` to `5.98`; for TCN 24f, it drops from `1.35` to `0.00`.
- Tradeoff: smoothing improves stability but increases observed MotionBERT switch delay p90 from `0.330s` to `0.736s`; TCN 24f did not show added delay in this quick-probe replay.
