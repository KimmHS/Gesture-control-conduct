# Goal Report 31 - Model Score Gate

## Purpose

현재까지는 score table을 사람이 읽고 GO/NO-GO를 판단했다. 최종 stream 모델 선택에서는 이 방식이 위험하므로, `scores.json`과 optional detailed eval JSON을 읽어 자동으로 pass/fail을 내는 score gate를 추가했다.

이 gate는 특히 target80 augmentation처럼 한 class recall은 좋아지지만 120 BPM이 collapse되는 경우를 막기 위한 장치다.

## Implemented Files

```text
lib/right_conducting/score_gate.py
tools/check_right_conducting_score_gate.py
tests/test_score_gate.py
```

Updated:

```text
tools/run_right_conducting_goal.py
tests/test_goal_command_cli.py
```

New runner step:

```text
gate
```

## Default Pass Line

| check | threshold |
|---|---:|
| cv_tempo_acc | >= 0.70 |
| cv_gain_acc | >= 0.95 |
| transition_tempo_acc | >= 0.60 |
| transition_bpm_mae_window | <= 10.0 |
| transition_gain_acc | >= 0.80 |
| tempo_80_recall | >= 0.50 if support > 0 |
| tempo_120_recall | >= 0.50 if support > 0 |

Notes:

```text
cv_mean alone is not enough.
transition heldout stability is required.
per-class recall is checked only when detailed eval JSON is provided.
For final model selection, use --require-detailed.
```

## Current Candidate Gate

Command:

```bash
python tools/check_right_conducting_score_gate.py \
  --score-json outputs/right_conducting/motionbert_head_v0_60f_stats_target80_combo_stride3_e80_h512_eval60stable/scores.json \
  --detailed-json outputs/right_conducting/motionbert_stats_target80_combo_stride3_eval60stable_detailed.json \
  --require-detailed \
  --output-json outputs/right_conducting/model_gate_current_motionbert_target80_combo_stride3.json \
  --output-md outputs/right_conducting/model_gate_current_motionbert_target80_combo_stride3.md
```

Result:

```text
status: NO_GO
```

Checks:

| check | value | threshold | passed |
|---|---:|---:|---|
| cv_tempo_acc | 0.7497 | >= 0.70 | true |
| cv_gain_acc | 0.9930 | >= 0.95 | true |
| transition_tempo_acc | 0.3539 | >= 0.60 | false |
| transition_bpm_mae_window | 16.2140 | <= 10.0 | false |
| transition_gain_acc | 0.7984 | >= 0.80 | false |
| tempo_80_recall | 0.8182 | >= 0.50 | true |
| tempo_120_recall | 0.0142 | >= 0.50 | false |

Interpretation:

```text
The gate catches the known failure:
target80 combo recovers 80 BPM recall but collapses true 120 BPM windows.
Therefore this MotionBERT head remains NO-GO as selected live model.
```

## After-Supply Gate Command

After new dataset cache/train:

```bash
python tools/run_right_conducting_goal.py \
  --steps gate \
  --head-output-dir outputs/right_conducting/motionbert_head_after_supply \
  --window-frames 60 \
  --gate-detailed-json outputs/right_conducting/motionbert_after_supply_eval60stable_detailed.json \
  --gate-require-detailed \
  --gate-output-prefix outputs/right_conducting/model_gate_after_supply
```

This expands to:

```bash
python tools/check_right_conducting_score_gate.py \
  --score-json outputs/right_conducting/motionbert_head_after_supply_60f/scores.json \
  --detailed-json outputs/right_conducting/motionbert_after_supply_eval60stable_detailed.json \
  --require-detailed \
  --output-json outputs/right_conducting/model_gate_after_supply_60f.json \
  --output-md outputs/right_conducting/model_gate_after_supply_60f.md
```

Dry-run artifact:

```text
outputs/right_conducting/right_conducting_goal_run_after_supply_gate_dryrun.json
outputs/right_conducting/right_conducting_goal_run_after_supply_gate_dryrun.md
```

## Gate Decision

```text
score gate implementation: GO
current MotionBERT target80 combo head: NO-GO
selected live fallback: unchanged
next after supplied data: prepare -> cache -> train -> detailed eval -> gate
```

## Verification

```bash
python -m unittest discover -s tests -p 'test_score_gate.py' -v
python -m unittest discover -s tests -p 'test_goal_command_cli.py' -v
python tools/check_right_conducting_score_gate.py --score-json ... --detailed-json ... --require-detailed
```

Result:

```text
score gate tests OK
goal command gate dry-run tests OK
current candidate NO-GO sanity OK
```
