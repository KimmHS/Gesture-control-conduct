# Mid-Presentation / Review Feedback Mapping

이 문서는 발표/리뷰 피드백이 최종 실험 설계에 어떻게 반영됐는지 추적하기 위한 파일이다.

## Feedback Summary

| Feedback | Decision |
|---|---|
| 오른손은 global conducting, 왼손은 instrument-level control로 분리 | 최종 구조에 반영. 왼손은 딥러닝 입력에서 제외하고 rule-based UI로 유지 |
| 데이터가 작아 hard classification만으로는 취약 | `tempo_class` 외에 `bpm_distribution` soft target을 KL loss로 학습 |
| dynamics는 class보다 연속 제어가 MIDI expression에 적합 | `dynamics`를 `0.0~1.0` regression으로 변경 |
| augmentation을 미루면 작은 데이터 한계가 큼 | v0에 temporal stretch와 amplitude scaling 포함. label도 함께 갱신 |
| take-level split은 single-subject generalization을 보장하지 않음 | model card/results에 single-subject 한계 명시. 최종은 multi-subject 또는 leave-one-subject-out 권장 |
| transition evaluation session이 부족함 | 현재 score 가능한 session은 early heldout으로만 취급. stable hold 3 takes + transition 2~3 takes 추가 권장 |
| live policy가 실제 predictor에 연결되어야 함 | `streaming_laptop.yaml`을 runtime predictor가 읽고 EMA/hysteresis/fast switch를 적용하도록 명시 |
| MotionBERT head가 모든 17 joint token을 flatten하면 noise가 큼 | default head는 right-arm token pooling. context ablation만 별도 비교 |
| MotionBERT frame length mismatch 검증 필요 | `T=60/120/180` smoke test를 필수로 추가 |
| rule-based baseline이 결과표에 필요 | `right_rule_features.npy` 기반 rule baseline을 score table required row로 추가 |
| 작은 ML baseline이 필요 | hand-crafted feature ML baseline을 required row로 추가 |
| checkpoint filename에 공백/괄호가 있어 shell에서 취약 | `checkpoint/mb_lite_v0.pt` symlink를 사용 |
| monolithic goal command는 실험 반복에 불편 | `--skip-*`, `--models`, `--folds`, `--normalizations`, `--window-frames` partial flags 추가 |

## Current Canonical Plan

```text
docs/exp/final_plan_motionbert_lite_conducting_control.md
```

## Current Non-Scoreable Eval

```text
dataset/evaluation_transitions/session_20260616_215630_eval
```

이 session은 실제 tempo transition이 있었지만 현재 labels가 constant label이라 relabel 전까지 score에서 제외한다.
