# Selected MotionBERT Live Policy Sweep

## Scope

```text
date: 2026-06-17
bundle: outputs/right_conducting/selected_motionbert_static80_transitions_live45f
replay_rows: outputs/right_conducting/selected_motionbert_static80_transitions_live45f/replay_transitions_stable_rows.jsonl
eval_root: dataset/transitions
window_frames: 45
stride_frames: 3
fps: about 15
```

## Command

```bash
python tools/sweep_motionbert_live_policy.py \
  --rows outputs/right_conducting/selected_motionbert_static80_transitions_live45f/replay_transitions_stable_rows.jsonl \
  --manifest outputs/right_conducting/selected_motionbert_static80_transitions_live45f/motionbert_conducting_live_manifest.json \
  --switch-thresholds 0.58,0.65,0.72,0.80,0.88 \
  --fast-switch-thresholds 0.78,0.85,0.90,0.95,0.99 \
  --confirm-updates 2,3,4,5 \
  --max-accuracy-drop 0.01 \
  --output-json outputs/right_conducting/selected_motionbert_static80_transitions_live45f/policy_sweep_transitions_stable.json \
  --output-md outputs/right_conducting/selected_motionbert_static80_transitions_live45f/policy_sweep_transitions_stable.md \
  --output-selected-rows outputs/right_conducting/selected_motionbert_static80_transitions_live45f/replay_transitions_stable_policy_selected_rows.jsonl
```

## Result

| policy | switch_threshold | fast_switch_threshold | confirm | tempo_acc | gain_acc | true_switch | pred_switch | false_switch | false/min | missed | p90 delay |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| baseline | 0.58 | 0.78 | 2 | 0.9893 | 1.0000 | 14 | 22 | 4 | 0.7971 | 0 | 0.0000 |
| selected | 0.72 | 0.90 | 2 | 0.9893 | 1.0000 | 14 | 14 | 0 | 0.0000 | 0 | 0.5938 |

## Final Replay Check

After updating the manifest policy, the full-backbone replay was rerun.

| eval_root | sessions | rows | mode | tempo_acc | gain_acc | false/min | missed | p90 delay |
|---|---:|---:|---|---:|---:|---:|---:|---:|
| dataset/static_variants_80 | 4 | 942 | smoothed | 1.0000 | 1.0000 | 0.0000 | 0 | 0.0000 |
| dataset/transitions | 7 | 1305 | smoothed | 0.9893 | 1.0000 | 0.0000 | 0 | 0.5938 |

## Interpretation

The policy change removes the remaining live false switches without lowering aggregate tempo accuracy on the current fixed-camera transition set. The tradeoff is controlled delay: p90 switch delay becomes about 0.59s.

The weakest remaining runtime case is no longer extra switching. It is delayed adaptation in:

```text
session_20260617_022517_bpm120to120_beat3_small
```

This is `120 -> 80 -> 120`, 3-beat, small dynamics. If more dev data is supplied, this condition should be the first independent heldout case.

## Artifacts

```text
outputs/right_conducting/selected_motionbert_static80_transitions_live45f/policy_sweep_transitions_stable.json
outputs/right_conducting/selected_motionbert_static80_transitions_live45f/policy_sweep_transitions_stable.md
outputs/right_conducting/selected_motionbert_static80_transitions_live45f/replay_transitions_stable.json
outputs/right_conducting/selected_motionbert_static80_transitions_live45f/replay_static80_stable.json
outputs/right_conducting/selected_motionbert_static80_transitions_live45f/motionbert_conducting_live_manifest.json
outputs/right_conducting/selected_motionbert_static80_transitions_live45f/motionbert_conducting_live_structure.md
```
