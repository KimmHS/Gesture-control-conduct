# Goal Status Dashboard

## Scope

```text
date: 2026-06-17
selected bundle: outputs/right_conducting/selected_motionbert_static80_transitions_live45f
manifest: outputs/right_conducting/selected_motionbert_static80_transitions_live45f/motionbert_conducting_live_manifest.json
```

## Added Tooling

```text
lib/right_conducting/goal_status.py
tools/summarize_right_conducting_goal_status.py
tests/test_goal_status.py
```

The dashboard reads the selected manifest and linked artifacts:

```text
deployment live replay gate
strict heldout live replay gate
heldout independence audit
full-backbone benchmark
model/checkpoint/config paths
```

## Command

```bash
python tools/summarize_right_conducting_goal_status.py \
  --manifest outputs/right_conducting/selected_motionbert_static80_transitions_live45f/motionbert_conducting_live_manifest.json \
  --output-json outputs/right_conducting/goal_status_selected_motionbert_live45f.json \
  --output-md outputs/right_conducting/goal_status_selected_motionbert_live45f.md
```

## Result

| status | live pilot | strict heldout |
|---|---|---|
| IN_PROGRESS | GO | NO_GO |

Model:

| field | value |
|---|---:|
| window_frames | 45 |
| stride_frames | 3 |
| fps | 15.0 |
| hidden_dim | 512 |
| feature_dim | 2048 |
| switch_threshold | 0.72 |
| fast_switch_threshold | 0.90 |

Gate summary:

| gate | status | tempo_acc | gain_acc | false/min | missed | p90 delay |
|---|---|---:|---:|---:|---:|---:|
| deployment-fit | GO | 0.9893 | 1.0000 | 0.0000 | 0 | 0.5938 |
| strict heldout | NO_GO | 0.9893 | 1.0000 | 0.0000 | 0 | 0.5938 |

Benchmark:

| pass | p90_ms | max_ms | headroom |
|---|---:|---:|---:|
| true | 12.1389 | 16.0964 | 16.4759 |

Strict heldout failure:

```text
heldout_independence_go: NO_GO
strict_live_gate_go: NO_GO
```

## Interpretation

The exported 45f MotionBERT bundle is usable for the fixed-camera live pilot. It has the model files, passes the deployment live replay gate, and passes the RTX 3090 streaming budget.

The full goal is not closed because strict heldout is not proven. The current transition/static score roots overlap with the staged training manifest, so the strict gate remains `NO_GO`.

## Next Action

```text
1. Record or point to fixed-camera heldout roots not included in the staged training manifest.
2. Run heldout-independence and require GO.
3. Run replay-selected + live-replay-gate with --live-replay-gate-require-independence.
```

## Artifacts

```text
outputs/right_conducting/goal_status_selected_motionbert_live45f.json
outputs/right_conducting/goal_status_selected_motionbert_live45f.md
```
