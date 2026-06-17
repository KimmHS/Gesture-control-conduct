# TCN Right Conducting Quick Probe

```text
model_type: causal_tcn_right_arm_pose
scope: deployment_fit_quick_probe
roots: dataset/static_variants_80,dataset/transitions
checkpoint: outputs/right_conducting/tcn_boundary0p5_shortwin_quick_probe_20260617/24f/tcn_conducting_head.pt
window_frames: 24
train_samples: 2346
```

| margin | samples | raw tempo | raw precision | raw recall | raw f1 | smooth tempo | smooth gain | false/min | missed | r80 | r100 | r120 | bpm mae |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.0 | 2410 | 0.9929 | 0.9905 | 0.9946 | 0.9925 | 0.9925 | 1.0000 | 2.6998 | 0 | 0.9916 | 0.9964 | 0.9928 | 0.2490 |
| 0.5 | 2346 | 0.9996 | 0.9998 | 0.9995 | 0.9996 | 1.0000 | 1.0000 | 0.0000 | 0 | 1.0000 | 1.0000 | 1.0000 | 0.0000 |
| 1.0 | 2282 | 0.9996 | 0.9998 | 0.9995 | 0.9996 | 1.0000 | 1.0000 | 0.0000 | 0 | 1.0000 | 1.0000 | 1.0000 | 0.0000 |

## Notes

- Quick TCN probe trains and evaluates on the same fixed-camera static80/transitions processed roots.
- Mixed BPM windows and configured boundary-jitter windows are excluded from training.
- Mixed BPM windows are excluded from margin scoring.
- Use this as a fast TCN comparison, not as strict heldout evidence.
