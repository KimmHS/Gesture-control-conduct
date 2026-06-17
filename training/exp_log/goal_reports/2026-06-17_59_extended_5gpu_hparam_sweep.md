# Extended 5-GPU Hparam Sweep

## Scope

```text
date: 2026-06-17
gpu_workers: 5
initial_candidates: 20
extended_candidates: 34
total_candidates: 54
eval_roots: dataset/static_variants_80, dataset/transitions
transition_margin_seconds: 3
fps_assumption: 15
tempo_bins: 60 / 80 / 100 / 120
```

The sweep uses the fixed-camera development data, including 2-beat and 3-beat
transition/static-80 sessions. Local eval augmentation folders are not used for
scoring.

## Main Result

The new fast live primary is:

```text
tag: ext_e240_h512_lr3e3_s0_45f
window_frames: 45
window_seconds: about 3.0s at 15fps
epochs: 240
hidden_dim: 512
lr: 0.003
dropout: 0.1
weight_decay: 0.001
seed: 0
checkpoint: outputs/right_conducting/motionbert_head_static80_transitions_ext_e240_h512_lr3e3_s0_45f/all_train_head.pt
```

The conservative accuracy top is:

```text
tag: ext_e240_h512_lr3e3_s0_60f
window_frames: 60
window_seconds: about 4.0s at 15fps
transition_tempo_acc: 1.0000
transition_bpm_mae_window: 0.0000
smoothed_false_switches_per_min: 0.0000
```

The 60-frame candidate is slightly cleaner offline, but the selected 45-frame
candidate is the better live-change tradeoff because it uses one second less
context and still keeps transition/stability metrics effectively saturated.

## Score Table

| candidate | window | samples | tempo_acc | bpm_mae | gain_acc | r80 | r100 | r120 | false/min | p90 delay |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| ext_e240_h512_lr3e3_s0_45f | 45 | 884 | 0.9989 | 0.0226 | 1.0000 | 0.9953 | 1.0000 | 1.0000 | 0.0000 | 0.0000 |
| ext_e240_h512_lr3e3_s0_60f | 60 | 779 | 1.0000 | 0.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | 0.0000 |

Full-backbone replay of the exported 45f bundle:

| eval_root | sessions | rows | smoothed tempo_acc | smoothed gain_acc | false/min | missed | p90 delay |
|---|---:|---:|---:|---:|---:|---:|---:|
| dataset/static_variants_80 | 4 | 942 | 1.0000 | 1.0000 | 0.0000 | 0 | 0.0000 |
| dataset/transitions | 7 | 1305 | 1.0000 | 1.0000 | 0.0000 | 0 | 0.0000 |

Benchmark:

| device | windows | update_budget_ms | end_to_end_p90_ms | max_ms | headroom | status |
|---|---:|---:|---:|---:|---:|---|
| cuda:3 | 1305 | 200.0000 | 11.6339 | 19.5126 | 17.1911 | PASS |

## Exported Bundle

```text
export_dir: outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext
manifest: outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/motionbert_conducting_live_manifest.json
structure: outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/motionbert_conducting_live_structure.md
head_checkpoint: outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/motionbert_conducting_head.pt
deployment_gate: outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/live_replay_gate_transitions_deployment.json
goal_status: outputs/right_conducting/goal_status_selected_motionbert_live45f_ext.json
```

## Artifacts

```text
outputs/right_conducting/hparam_sweep_static80_transitions_extended_20260617.json
outputs/right_conducting/hparam_sweep_static80_transitions_extended_20260617.md
outputs/right_conducting/model_candidate_selection_ext_live45f.json
outputs/right_conducting/model_candidate_selection_ext_live45f.md
outputs/right_conducting/hparam_ext_logs_20260617/
```

## Interpretation

The extended sweep fixes the previous uncertainty around whether the 45-frame
candidate was lucky. Multiple nearby settings remain strong, and the selected
45f candidate improves the old 45f row while preserving faster response.

The current result should be used as fixed-camera deployment-fit evidence. It is
not strict heldout generalization because `dataset/static_variants_80` and
`dataset/transitions` are part of the training/staged source for this selected
bundle.

## Remaining Gap

```text
live_pilot_status: GO
strict_heldout_status: NO_GO
reason: no independent heldout transition/static root has been replayed with independence required
next: record a heldout fixed-camera transition set outside the staged training manifest and rerun strict heldout replay/gate
```
