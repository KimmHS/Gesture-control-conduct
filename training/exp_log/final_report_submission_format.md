# Final Report Submission Format

이 파일은 최종 리포트의 큰 제목, 소제목, 확정된 세부 내용만 정리한다.

## 1. Task 설명

### 1.1 목표

- 오른손 지휘 동작으로 MIDI playback의 tempo와 dynamics를 실시간 제어한다.
- 입력은 webcam video에서 추출한 pose sequence이다.
- 출력은 `tempo`와 `dynamics`이다.

### 1.2 제어 대상

| output | 의미 | MIDI 연결 |
|---|---|---|
| tempo | 지휘 속도에 해당하는 BPM class | playback tempo |
| dynamics | 지휘 동작 크기/세기 | velocity scale 또는 CC11 Expression |

## 2. Demo

### 2.1 제출 방식

- 영상과 함께 제출한다.
- 영상에는 입력 동작, 예측 결과, MIDI 반응이 함께 보이도록 한다.

### 2.2 Demo 구성

| demo | 내용 |
|---|---|
| basic control | 안정적인 tempo / dynamics 제어 |
| free change evaluation | 5초~10초마다 tempo 또는 dynamics 변경 |
| transition challenge | tempo switching 지점에서 발생하는 문제와 처리 결과 |

### 2.3 영상 Overlay 항목

- true BPM
- predicted BPM
- true dynamics
- predicted dynamics/gain
- raw prediction
- smoothed prediction
- window size

## 3. Spec 정리

### 3.1 현재 v0 범위

| item | 확정 내용 |
|---|---|
| pose fps | 약 15 fps |
| tempo classes | 60 / 80 / 100 / 120 BPM |
| default window | 60 frames, 약 4초 |
| default stride | 3 frames, 약 0.2초 |
| realtime output | tempo / dynamics |

### 3.2 Final Target 범위

| item | 확정 내용 |
|---|---|
| tempo classes | 60 / 80 / 100 / 120 / 140 / 160 BPM로 확장 예정 |
| evaluation style | 자유롭게 5초~10초마다 요소 변경 |
| evaluation duration | 약 1분 |
| evaluation subjects | 5명 |
| takes per subject | 5개 |

## 4. Method

### 4.1 Tempo, Dynamics

#### 4.1.1 Rule-Based

- 오른손 trajectory feature를 사용한다.
- tempo는 wrist trajectory의 periodicity / FFT 기반으로 추정한다.
- dynamics는 shoulder-wrist amplitude 또는 motion radius 기반으로 추정한다.
- rule-based method는 baseline과 live fallback으로 사용한다.

#### 4.1.2 Deep-Learning

- current selected live model은 causal TCN right-arm pose classifier다.
- 입력은 right shoulder / right elbow / right wrist의 45-frame window다.
- 출력은 tempo class와 gain class다.
- MotionBERT-Lite frozen encoder + conducting head는 comparison 후보로 기록한다.

### 4.2 Deep-Learning Pipeline

```text
webcam / handmark CSV stream
  -> right shoulder / right elbow / right wrist
  -> H36M17 right-arm masked sequence
  -> sliding window [B, 45, 17, 3]
  -> causal TCN
  -> tempo class / gain class
  -> live smoother
  -> MIDI tempo / velocity / CC11
```

## 5. Dataset

### 5.1 현재 Dataset 구성

| root | 용도 | 확정 상태 |
|---|---|---|
| `dataset/recordings` | stable train | 24 sessions scoreable |
| `dataset/static_variants_80` | fixed-camera 80 BPM static stress | 4 sessions scoreable |
| `dataset/transitions` | fixed-camera transition stress | 7 transition sessions scoreable, 11 total with static variants |
| `dataset/evaluation_transitions/session_20260616_215630_bpm100_beat4_large` | pending eval | relabel/timeline 필요 |
| `dataset/strict_heldout_static_v1` | strict independent static heldout | not supplied |
| `dataset/strict_heldout_transitions_v1` | strict independent transition heldout | not supplied |

### 5.2 `dataset/transitions` 구성

| sequence | sessions |
|---|---:|
| 120 -> 80 -> 120 | 7 |
| 100 -> 80 -> 100 | 4 |

| dynamics prompt | sessions |
|---|---:|
| large | 6 |
| small | 5 |

### 5.3 최종 Evaluation Set 조건

| condition | 확정 내용 |
|---|---|
| change interval | 5초~10초 |
| take length | 약 1분 |
| subject count | 5명 |
| takes per subject | 5개 |
| total takes | 25개 |
| changed factors | tempo / dynamics |

## 6. Model Structure

### 6.1 Input

```text
x_body: [B, T, 17, 3]
channels: x, y, confidence
```

### 6.2 Window Size

현재 실험 window size:

| window size | 약 시간 |
|---:|---:|
| 30 frames | 약 2초 |
| 45 frames | 약 3초 |
| 60 frames | 약 4초 |
| 90 frames | 약 6초 |
| 120 frames | 약 8초 |

### 6.3 Backbone

- current selected model은 MotionBERT backbone을 사용하지 않는다.
- causal residual Conv1d TCN이 right-arm 45-frame sequence를 직접 입력받는다.
- MotionBERT-Lite frozen encoder는 comparison / research baseline으로 유지한다.

### 6.4 Conducting Head

- TCN encoder output을 temporal mean pooling한다.
- tempo head는 4-class BPM logits를 출력한다.
- gain head는 small / large 2-class logits를 출력한다.
- live smoother가 raw logits를 MIDI-ready tempo/gain output으로 변환한다.

## 7. Challenge

### 7.1 문제

Dataset에서 tempo가 switching되는 부분에서 문제가 발생한다.

확정된 문제:

| problem | 내용 |
|---|---|
| transition boundary ambiguity | window가 전환 전/후 frame을 동시에 포함하면 label이 애매해진다 |
| mixed-window label issue | transition 근처 window는 하나의 BPM label로 보기 어렵다 |
| stable-tail failure | transition margin을 제거해도 80 BPM tail을 제대로 맞히지 못한다 |
| domain/session dependency | eval set에 따라 80 또는 120 class가 붕괴한다 |
| class imbalance | gain accuracy만 보면 좋아 보이나 small/large support 차이가 있다 |

### 7.2 해결 방향

확정된 처리:

| solution | 내용 |
|---|---|
| stable-window scoring | mixed BPM window를 제외하고 평가 |
| transition margin sweep | 0.0 / 0.5 / 1.0 / 2.0 / 3.0초 margin별 평가 |
| per-class metrics | 60/80/100/120 및 small/large별 precision, recall, F1 확인 |
| dataset intake gate | stable train과 transition eval을 분리 |
| smoothing/replay evaluation | raw/smoothed prediction을 따로 평가 |

## 8. Result

### 8.1 Evaluation Set

최종 리포트에서는 아래 evaluation set 조건을 사용한다.

| item | 확정 내용 |
|---|---|
| subject count | 5명 |
| takes per subject | 5개 |
| take duration | 약 1분 |
| change interval | 5초~10초 |
| changed factors | tempo / dynamics |

### 8.2 Metric

최종 리포트에 포함할 metric:

| metric | target |
|---|---|
| accuracy | tempo / gain |
| precision | tempo class / gain class |
| recall | tempo class / gain class |
| F1 | tempo class / gain class |
| MAE | BPM / dynamics |
| false switches per minute | streaming |
| switch delay | streaming |
| missed switches | streaming |

### 8.3 Target Score

최종 리포트에서 제시할 목표 score:

| target | 기준 |
|---|---:|
| CV tempo accuracy | >= 0.70 |
| CV gain accuracy | >= 0.95 |
| transition tempo accuracy | >= 0.60 |
| transition BPM MAE | <= 10.0 |
| transition gain accuracy | >= 0.80 |
| tempo 80 recall | >= 0.50 |
| tempo 120 recall | >= 0.50 |
| false switches per minute | selected fallback 이하 |
| switch delay p90 | selected fallback 이하 |

GO / NO-GO 기준:

| label | 의미 |
|---|---|
| selected | 현재 live/export에 사용하는 모델 |
| GO | 목표 score를 모두 만족한 후보 |
| NO_GO | 하나 이상의 목표 score를 만족하지 못한 후보 |
| DIAG_ONLY | 진단용 결과이며 live 후보가 아님 |

### 8.4 Table

최종 리포트에 포함할 표:

| table | 내용 |
|---|---|
| Overall Model Comparison | rule-based, feature baseline, MotionBERT, selected TCN 비교 |
| Window Size Sweep | 30 / 45 / 60 / 90 / 120 frames별 score |
| Transition Margin Sweep | 0.0 / 0.5 / 1.0 / 2.0 / 3.0초 margin별 score |
| Per-Class Tempo Metrics | 60 / 80 / 100 / 120별 precision, recall, F1, support |
| Per-Class Dynamics/Gain Metrics | small / large별 precision, recall, F1, support |
| Streaming Replay | raw / smoothed prediction의 live-style score |

### 8.5 Current Selected TCN Result

현재 제출 가능한 live-facing 결과:

```text
report: docs/exp/goal_reports/2026-06-17_117_full_test_release_and_status_rerun.md
score: outputs/right_conducting/tcn_alltest_latest/stream_set_score_fulltest_latest.json
gate: outputs/right_conducting/tcn_alltest_latest/stream_set_gate_fulltest_latest.json
current_status: outputs/right_conducting/tcn_alltest_latest/current_status_fulltest_latest.json
model_card: docs/exp/right_hand_conducting_model_card.md
handoff: docs/exp/tcn_live_handoff_runbook.md
```

| item | value |
|---|---:|
| selected model | causal TCN right-arm pose classifier |
| discovered raw CSV files | 15 |
| scoreable processed sessions | 11 |
| transition margin | 3.0 s |
| sample count | 1824 |
| tempo accuracy | 1.0000 |
| gain accuracy | 1.0000 |
| 80 / 100 / 120 recall | 1.0000 / 1.0000 / 1.0000 |
| BPM MAE | 0.0000 |
| false switches / min | 0.0000 |
| missed switches | 0 |
| switch delay p90 | 0.0000 s |
| runtime p90 | 1.9984 ms |

Interpretation:

```text
fixed-camera supplied-set live pilot: GO
release validation: GO
strict independent heldout: NO_GO, P0 0/8
overall goal status: IN_PROGRESS
```

## 9. Graph

최종 리포트에 포함할 그래프:

| figure | 내용 |
|---|---|
| window_size_vs_score | window size별 accuracy / F1 / MAE |
| margin_vs_score | transition margin별 accuracy / recall / MAE |
| confusion_matrix | tempo class confusion |
| per_class_f1_bar | class별 F1 |
| true_pred_timeline | 시간축 true/pred tempo 비교 |
| gain_timeline | 시간축 true/pred dynamics 비교 |
| per_session_heatmap | session별 metric 차이 |

## 10. 제출 체크리스트

| item |
|---|
| Task 설명 |
| Demo 영상 |
| Rule-based method |
| Deep-learning method |
| Dataset |
| Model structure |
| Challenge |
| Evaluation set |
| Metric |
| Result table |
| Graph |
