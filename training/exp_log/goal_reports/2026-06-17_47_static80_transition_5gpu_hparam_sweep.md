# Static80 + Transition 5-GPU Hparam Sweep

## Scope

```text
date: 2026-06-17
train_source: outputs/right_conducting/recordings_staged_static80_transitions.zip
static_eval: dataset/static_variants_80
transition_eval: dataset/transitions
fps: about 15
tempo_bins: 60 / 80 / 100 / 120
transition_gate_margin_seconds: 3
score_policy: original eval artifacts only; eval-local augmentation excluded
```

## Dataset Fix

`labels_frame.jsonl`의 numeric `dynamics` 값이 large/small prompt와 다를 수 있어서, train window 생성 시 `dynamics_condition`이 있으면 gain target은 take/frame condition을 우선 사용하도록 수정했다.

검증:

```text
python -m unittest discover -s tests -p 'test_right_conducting_dataset_prep.py' -v
python -m unittest discover -s tests -p 'test_goal_command_cli.py' -v
```

## Sweep

5개 GPU에 window length를 나눠서 실행했다.

```text
windows: 30 / 45 / 60 / 90 / 120 frames
configs:
  e160_h512_lr1e3
  e120_h256_lr1e3
  e200_h512_lr3e4
  e120_h512_lr3e3
```

Full result:

```text
outputs/right_conducting/hparam_sweep_static80_transitions_20260617.json
outputs/right_conducting/hparam_sweep_static80_transitions_20260617.md
```

## Decision

Primary live candidate:

```text
tag: static80_transitions_e120_h512_lr3e3
window_frames: 45
window_seconds: about 3.0s at 15fps
head_checkpoint: outputs/right_conducting/motionbert_head_static80_transitions_e120_h512_lr3e3_45f/all_train_head.pt
transition_tempo_acc: 0.9943
transition_80_recall: 0.9810
transition_100_recall: 0.9948
transition_120_recall: 1.0000
transition_gain_acc: 1.0000
bpm_mae_window: 0.1131
smoothed_false_switches_per_min: 0.1993
smoothed_switch_delay_p90_s: 0.0
```

Conservative fallback:

```text
tag: static80_transitions_e160_h512_lr1e3
window_frames: 60
window_seconds: about 4.0s at 15fps
head_checkpoint: outputs/right_conducting/motionbert_head_static80_transitions_e160_h512_lr1e3_60f/all_train_head.pt
transition_tempo_acc: 0.9936
transition_80_recall: 0.9886
transition_100_recall: 0.9884
transition_120_recall: 0.9977
transition_gain_acc: 1.0000
bpm_mae_window: 0.1284
smoothed_false_switches_per_min: 0.0
smoothed_switch_delay_p90_s: 0.0
```

120f rows can score slightly higher, but 120 frames is about 8 seconds on current data, so they are not selected as the live primary.

## Export

Selected bundle:

```text
outputs/right_conducting/selected_motionbert_static80_transitions_live45f/motionbert_conducting_live_manifest.json
outputs/right_conducting/selected_motionbert_static80_transitions_live45f/motionbert_conducting_live_structure.md
outputs/right_conducting/selected_motionbert_static80_transitions_live45f/motionbert_conducting_head.pt
```

Smoke:

```text
outputs/right_conducting/selected_motionbert_static80_transitions_live45f/smoke_head_only.json
```

## Remaining Risk

`dataset/transitions` was included in the deployment-fit training source, so these scores prove current fixed-camera transition controllability, not independent generalization. If a stricter heldout claim is needed, record another fixed-camera transition set and keep it out of training.
