# Selected MotionBERT Live Benchmark

## Scope

```text
date: 2026-06-17
bundle: outputs/right_conducting/selected_motionbert_static80_transitions_live45f
manifest: outputs/right_conducting/selected_motionbert_static80_transitions_live45f/motionbert_conducting_live_manifest.json
eval_root: dataset/transitions
device: cuda:2
window_frames: 45
stride_frames: 3
fps: 15
update_interval_ms: 200
stable_only: true
```

## Pass Line

```text
end_to_end_window_ms.p90 < stride_frames / fps
```

At 15fps and stride 3, the model gets a new decision every about 200ms. The full runtime path must finish one window inference below that budget.

## Command

```bash
python tools/benchmark_motionbert_live_bundle.py \
  --manifest outputs/right_conducting/selected_motionbert_static80_transitions_live45f/motionbert_conducting_live_manifest.json \
  --eval-root dataset/transitions \
  --device cuda:2 \
  --stable-only \
  --warmup-windows 20 \
  --output-json outputs/right_conducting/selected_motionbert_static80_transitions_live45f/benchmark_transitions_stable.json \
  --output-md outputs/right_conducting/selected_motionbert_static80_transitions_live45f/benchmark_transitions_stable.md
```

## Result

| stage | mean_ms | median_ms | p90_ms | p95_ms | max_ms |
|---|---:|---:|---:|---:|---:|
| predict_window | 10.9869 | 10.8173 | 12.1266 | 12.3823 | 16.0817 |
| smoother_update | 0.0111 | 0.0107 | 0.0130 | 0.0136 | 0.0360 |
| end_to_end | 10.9980 | 10.8290 | 12.1389 | 12.3940 | 16.0964 |

Budget:

```text
pass: true
update_interval_ms: 200.0
end_to_end_p90_ms: 12.1389
headroom_ratio: 16.4759
```

## Interpretation

The selected 45f MotionBERT bundle is fast enough for the current 15fps / stride 3 stream plan on RTX 3090.

The latency bottleneck is no longer full-backbone inference. The remaining live risk is model behavior in the weak edge case:

```text
120 -> 80 -> 120 / 3-beat / small dynamics
```

That should be the next heldout/devset priority if more data is supplied.

## Artifacts

```text
outputs/right_conducting/selected_motionbert_static80_transitions_live45f/benchmark_transitions_stable.json
outputs/right_conducting/selected_motionbert_static80_transitions_live45f/benchmark_transitions_stable.md
```

The selected manifest and structure file now include benchmark evidence:

```text
outputs/right_conducting/selected_motionbert_static80_transitions_live45f/motionbert_conducting_live_manifest.json
outputs/right_conducting/selected_motionbert_static80_transitions_live45f/motionbert_conducting_live_structure.md
```
