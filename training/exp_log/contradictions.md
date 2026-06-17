# Current Contradictions To Keep Straight

이 문서는 goal 구현 전에 헷갈리기 쉬운 모순만 짧게 정리한다.
구현 방법, 개선안, 실험 순서는 적지 않는다.

## 1. FPS / Window

| 항목 | 현재 v0 | final target |
|---|---|---|
| FPS | 약 15fps | 30fps 또는 명시적 30fps resampling |
| 기본 window | 60 frames ~= 4s | 120 frames = 4s |
| 120-frame window | 현재 데이터에서는 ~= 8s ablation | 30fps 기준 기본값 |

결론: current v0 score는 `60 frames / stride 3`을 기본으로 보고한다. `120 frames = 4s`라고 쓰면 안 된다.

## 2. Tempo Class

| 항목 | 현재 v0 | final target |
|---|---|---|
| tempo bins | 60 / 80 / 100 / 120 | 60 / 80 / 100 / 120 / 140 / 160 |
| class count | 4-class | 6-class |

결론: v0 실험 결과표와 model card는 4-class로 쓴다. 140/160 BPM은 future scope다.

## 3. Tempo Output / Score

| 항목 | 현재 v0 구현/score | final target |
|---|---|---|
| MotionBERT head | `tempo_class` + `bpm_distribution` head 있음 | 유지 |
| feature/rule fallback | centroid class/probability 중심 | soft BPM distribution model 아님 |
| baseline score | `bpm_distribution_kl = None` 가능 | distribution head가 있을 때만 KL 보고 |

결론: feature fallback score를 final distribution model 결과처럼 쓰면 안 된다. `bpm_distribution_kl`은 MotionBERT/distribution head가 있을 때만 채운다.

## 4. Evaluation Set

| session | 현재 처리 |
|---|---|
| `session_20260616_222455_eval` | score 가능하지만 `33.0s` ambiguous timeline caveat 명시 |
| `session_20260616_215630_eval` | tempo transition relabel 전까지 score 제외 |

결론: transition latency, false switch 같은 live metric은 현재 heldout 수가 부족하므로 강한 결론으로 쓰지 않는다.

## 5. Evaluation Augmentation Artifacts

Evaluation folder 안에 아래 augmentation 산출물이 있어도 score에는 쓰지 않는다.

```text
recommended_augmented_v0/
labels_tempo_augmented_15f.jsonl
tempo_augmented_15f.npy
label_backup_*
```

결론: 평가 스크립트는 원본 `labels_window.jsonl`, `pose_right_h36m_masked.npy`, `right_rule_features.npy`만 읽어야 한다.

## 6. Dataset Generalization

현재 train set은 single-subject 또는 subject-specific일 가능성이 높다.

결론: take-level 3-fold 결과는 within-subject validation이다. cross-subject generalization으로 주장하지 않는다.

## 7. Selected Model

| 항목 | 현재 v0 | final target |
|---|---|---|
| selected live artifact | `handcrafted_feature_ml` fallback | MotionBERT-Lite frozen encoder + conducting head |
| MotionBERT status | CV는 가능하지만 heldout transition no-go | final deep model candidate |

결론: `feature_baseline_live_v0.json`은 live fallback이지 최종 딥러닝 모델 파라미터가 아니다.

## 8. Live Metrics

| 항목 | 현재 측정값 | 해석 |
|---|---|---|
| raw replay | model/fallback 자체 출력 | false switch 많음 |
| smoothed replay | selected policy 적용 후 출력 | switch delay 증가 |

결론: live score는 smoothing policy까지 포함한 controller score다. 모델 단독 성능처럼 쓰면 안 된다.

## 9. Live Policy Source

| 항목 | 현재 v0 | final target |
|---|---|---|
| policy source | artifact/CLI arguments의 `LivePolicy` | `streaming_laptop.yaml` 같은 config file |
| 문서 표현 | YAML policy를 runtime source처럼 설명하는 부분 있음 | 실제 replay/export와 동일한 source를 명시 |

결론: 현재 live metric은 YAML을 읽은 결과가 아니라 artifact/CLI policy로 측정한 결과다. YAML runtime config가 구현되기 전까지 둘을 같은 것으로 쓰면 안 된다.

## 10. Goal Command

`scripts/run_right_conducting_goal.sh`는 현재 `audit/eval/replay/analyze` subset에 대해 실행 가능한 goal command다.

결론: 현재 점수 문서에는 검증된 subset만 executable command로 표시하고, cache/train/export 같은 비싼 단계는 별도 workflow로 구분한다.

## 11. Score / Model Card Status

| 문서 | 현재 상태 |
|---|---|
| `right_hand_conducting_scores.md` | baseline score와 MotionBERT-Lite pooled-head score는 있음; pooled-head tempo는 no-go |
| `right_hand_conducting_model_card.md` | final selected model card가 아니라 current candidate/fallback 기록 |

결론: 발표 보고서에는 pending과 measured를 분리해서 쓴다.

## 12. Dataset Input Space

| 문서/데이터 | 의미 |
|---|---|
| raw recording csv / handmark feature docs | 원본 recording 및 rule feature schema |
| `pose_right_h36m_masked.npy` | 딥러닝 입력 schema |

결론: raw csv schema를 MotionBERT input schema처럼 설명하면 안 된다.

## 13. MotionBERT Smoke Test

| 확인된 것 | 확인 안 된 것 |
|---|---|
| checkpoint load, `T=60/120` forward shape | heldout stability, final live suitability |

결론: smoke test 통과는 backbone 사용 가능성 확인이지 모델 성능 보장이 아니다.
