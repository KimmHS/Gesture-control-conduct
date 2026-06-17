# Report 38 — 5-GPU Hparam Sweep And Transition Stress

## Scope

새로 공급된 `dataset/transitions`를 scoreable transition stress set으로 intake하고, stable train set `dataset/recordings` 24 takes로 MotionBERT-Lite conducting head hparam sweep을 실행했다.

이번 run은 selected live model 교체가 아니라, 부족한 데이터/조건을 찾기 위한 진단 run이다.

## Dataset Intake

```text
train root: dataset/recordings
scoreable eval: dataset/evaluation/session_20260616_222455_bpm120_beat4_large
transition stress root: dataset/transitions
pending relabel: dataset/evaluation_transitions/session_20260616_215630_bpm100_beat4_large
```

Intake artifact:

```text
outputs/right_conducting/dataset_intake_after_transitions_schedule.json
outputs/right_conducting/dataset_intake_after_transitions_schedule.md
```

Result:

```text
train_ready: 24
heldout_transition_scoreable: 11
heldout_transition_pending_relabel: 1
```

`dataset/transitions`는 `meta.json`의 `bpm_schedule` 기준으로 scoreable이다. 각 take는 15s에 target BPM으로 바뀌고 30s에 source BPM으로 복귀한다. eval-local augmentation artifact는 모든 session 안에 있지만 score에서는 제외한다.

## Code Fixes

- `tools/*` default eval path를 실제 존재하는 `dataset/evaluation/session_20260616_222455_bpm120_beat4_large`로 수정했다.
- `lib/right_conducting/dataset_intake.py`가 `manual_timeline.json`뿐 아니라 `meta.json`의 transition `bpm_schedule`도 scoreable source로 인정하게 했다.
- `lib/right_conducting/eval_windows.py`가 frame label에 `dynamics_condition`이 없을 때 session `meta.json`의 large/small 조건을 사용하게 했다.
- `tools/run_right_conducting_goal.py`의 frame suffix helper가 `e120` 같은 epoch 문자열을 `120f` suffix로 오판하던 버그를 수정했다.
- regression metric의 상수 correlation이 `NaN`으로 JSON에 남지 않도록 0.0으로 처리했다.

## Sweep

Stage/prepare/cache baseline command:

```bash
python tools/run_right_conducting_goal.py \
  --steps stage,prepare,cache,train,detailed,gate,select \
  --train-roots dataset/recordings \
  --eval-roots dataset/evaluation_transitions,dataset/transitions \
  --stage-output-zip outputs/right_conducting/recordings_staged_hparam_base.zip \
  --dataset-dir outputs/right_conducting/hparam_base_dataset \
  --cache-dir outputs/right_conducting/hparam_base_cache_stats \
  --head-output-dir outputs/right_conducting/hparam_base_head_h512_lr1e3_e80 \
  --devices cuda:0,cuda:1,cuda:2,cuda:3,cuda:4 \
  --parallel-gpu \
  --cache-feature-mode mean_std_delta \
  --train-epochs 80 \
  --train-hidden-dim 512 \
  --train-lr 0.001 \
  --eval-session dataset/evaluation/session_20260616_222455_bpm120_beat4_large \
  --window-frames 30,45,60,90,120 \
  --stride-frames 3 \
  --gate-require-detailed
```

The first pass failed at eval because the old default eval path no longer existed. The cached features were valid and reused. The rerun used the corrected eval path:

```text
outputs/right_conducting/hparam_base_goal_h512_lr1e3_e80_rerun.json
```

Additional head-only hparam sweeps:

```text
h256_lr1e3_e120
h256_lr3e4_e120
h512_lr3e4_e120
h1024_lr3e4_e120
```

Logs:

```text
outputs/right_conducting/hparam_sweep_logs/
```

Summary artifacts:

```text
outputs/right_conducting/hparam_sweep_summary_20260617.json
outputs/right_conducting/hparam_sweep_summary_20260617.md
```

## Result

No MotionBERT hparam candidate passed the live gate.

Best rows on `222455` stable transition eval:

| rank | candidate | window | status | cv_acc | 222455_acc | bpm_mae | gain_acc | r80 | r120 |
|---:|---|---:|---|---:|---:|---:|---:|---:|---:|
| 1 | h512_lr3e4_e120 | 90 | NO_GO | 0.7424 | 0.3756 | 14.5540 | 0.7746 | 0.0000 | 0.0000 |
| 2 | h1024_lr3e4_e120 | 45 | NO_GO | 0.7285 | 0.3721 | 17.6744 | 0.7791 | 0.6250 | 0.0000 |
| 3 | h1024_lr3e4_e120 | 120 | NO_GO | 0.7451 | 0.3698 | 13.3333 | 0.8073 | NA | 0.0000 |
| 7 | h512_lr1e3_e80 | 30 | NO_GO | 0.6603 | 0.3407 | 19.7802 | 0.8278 | 0.8095 | 0.0000 |

The original 222455 eval consistently fails on `tempo_120_recall`.

Representative stress eval on `dataset/transitions`:

| candidate | window | margin | samples | acc | bpm_mae | gain_acc | r80 | r100 | r120 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| h1024_lr3e4_e120_120f | 120 | 3.0 | 570 | 0.5035 | 10.2105 | 0.8351 | 0.0000 | 0.3978 | 0.6554 |
| h512_lr1e3_e80_30f | 30 | 3.0 | 1560 | 0.4128 | 14.1026 | 0.9679 | 0.0000 | 0.3873 | 0.6430 |
| h512_lr3e4_e120_90f | 90 | 3.0 | 900 | 0.4556 | 11.7778 | 0.9689 | 0.0000 | 0.3684 | 0.6710 |

The new transition stress set recovers 120 moderately but fails `tempo_80_recall = 0.0` even after a 3s margin.

## Interpretation

This is not mainly a smoothing problem. Transition-margin filtering improves overall accuracy but does not recover the missing class.

The failure is take/domain dependent:

- `222455`: candidates collapse away from 120 BPM.
- `dataset/transitions`: candidates collapse away from 80 BPM.

This implies the current representation is using take/camera/meter/dynamics cues too strongly and tempo cues too weakly. More head hparam tuning alone is unlikely to solve it.

## Next Devset Request

Minimum next useful data:

```text
80 static:
- 80 / 2박 / large / fixed camera / high arm
- 80 / 2박 / small / fixed camera / high arm
- 80 / 3박 / large / fixed camera / low arm
- 80 / 3박 / small / fixed camera / low arm
- 80 / 4박 / large / fixed camera / neutral arm
- 80 / 4박 / small / fixed camera / neutral arm

transition:
- 120 -> 80 -> 120 / 2박 / large
- 120 -> 80 -> 120 / 2박 / small
- 120 -> 80 -> 120 / 4박 / large
- 120 -> 80 -> 120 / 4박 / small
```

Reason:

- 80 static isolates whether the model can classify stable 80 at all under fixed-camera meter/dynamics variation.
- 120 -> 80 held transitions test whether the 80 tail is recognized after excluding transition-near windows.

## Gate

```text
MotionBERT selected replacement: NO
current selected fallback replacement: NO
next action: collect 80 static variants and 120->80 held transitions, then rerun intake/stage/prepare/cache/train/detailed/gate/select
```

## Verification

```bash
python -m unittest discover -s tests -p 'test_eval_windows.py' -v
python -m unittest discover -s tests -p 'test_dataset_intake.py' -v
python -m unittest discover -s tests -p 'test_goal_command_cli.py' -v
python -m compileall -q lib/right_conducting tools tests
```

Status at report creation:

```text
python -m unittest discover -s tests -p 'test_*.py' -v: 116 OK
python -m compileall -q lib/right_conducting tools tests: OK
hparam_sweep_summary_20260617.json: strict JSON load OK
dataset_intake_after_transitions_schedule.json: strict JSON load OK
```
