# Presentation Summary: Right-Hand Conducting Model

## Slide 1. 연구 목표

오른손 지휘 동작 기반 MIDI 제어 모델을 만든다.

- 입력: 오른손 / 오른팔 움직임
- 출력: MIDI tempo, dynamics 제어
- 목표: webcam 기반 실시간 지휘 인터페이스
- 현재 범위: fixed-camera live pilot

핵심 주장:

```text
오른손 pose sequence만으로 tempo 변화와 dynamics를 실시간 제어할 수 있다.
```

## Slide 2. 전체 Pipeline

```text
Webcam / Handmark CSV
  -> right shoulder / elbow / wrist 추출
  -> H36M17 right-arm masked pose
  -> temporal model
  -> tempo class + gain class
  -> smoother
  -> MIDI tempo / velocity / CC11
```

출력:

- `tempo_class`: 60 / 80 / 100 / 120 BPM
- `gain_class`: small / large
- MIDI 연결:
  - tempo BPM
  - velocity scale
  - CC11 expression

## Slide 3. 왜 데이터셋을 추가로 요구했나

기존 문제:

- transition stress set에서 120 BPM은 회복했다.
- 하지만 transition 이후 80 BPM tail을 놓치는 현상이 있었다.
- 원인 분리가 필요했다.

확인해야 한 질문:

- 80 BPM 자체를 못 알아보는가?
- transition 직후라 어려운가?
- beat, arm height, dynamics 변화 때문인가?
- camera 조건 변화 때문인가?

따라서 추가 데이터는 단순 증량이 아니라 failure mode isolation 목적이었다.

## Slide 4. 수집한 데이터 구성

Static 80 BPM set:

```text
dataset/static_variants_80
80 BPM / 2 beat / large, small
80 BPM / 3 beat / large, small
fixed camera
high-arm / low-arm variant
```

Transition set:

```text
dataset/transitions
120 -> 80 -> 120
100 -> 80 -> 100
2/3 beat
large/small dynamics
```

평가에는 original artifacts만 사용했다.

```text
pose_right_h36m_masked.npy
labels_frame.jsonl
labels_window.jsonl
right_rule_features.npy
meta.json
```

Eval-local augmentation은 score에서 제외했다.

```text
recommended_augmented_v0/
labels_tempo_augmented_15f.jsonl
tempo_augmented_15f.npy
```

## Slide 5. Annotation 방식

Frame-by-frame 수동 labeling을 하지 않는다.

대신 녹화 protocol 자체를 label source로 사용한다.

```text
static take:
80 BPM / 2 beat / small

transition take:
0s: 120 BPM
15s: 80 BPM
30s: 120 BPM
46s: stop
```

자동 생성 label:

```text
bpm_target
tempo_class
meter_beats
dynamics_condition
gain_class
valid_right_arm_ratio
mixed_bpm_label
```

현재 v0 label space:

```text
tempo_class:
0 -> 60 BPM
1 -> 80 BPM
2 -> 100 BPM
3 -> 120 BPM

gain_class:
0 -> small
1 -> large
```

## Slide 6. Window Labeling

모델은 frame 단위가 아니라 window 단위로 학습한다.

현재 best live model 기준:

```text
fps: about 15
window_frames: 45  # 약 3초
stride_frames: 3   # 약 0.2초
```

Transition boundary를 걸치는 window는 mixed label로 표시한다.

```text
mixed_bpm_label = true
```

학습과 주요 score에서는 아래 조건만 사용한다.

```text
mixed_bpm_label == false
valid_right_arm_ratio >= 0.95
```

## Slide 7. Best Model

최신 live-facing best model:

```text
model: causal TCN right-arm pose classifier
bundle: outputs/right_conducting/selected_tcn_handmark_live45f
checkpoint: outputs/right_conducting/selected_tcn_handmark_live45f/tcn_conducting_head.pt
manifest: outputs/right_conducting/selected_tcn_handmark_live45f/tcn_conducting_live_manifest.json
```

입력:

```text
right shoulder / right elbow / right wrist
pose input: [B, 45, 17, 3]
TCN input: [B, 9, 45]
```

출력:

```text
tempo logits: 4 classes
gain logits: 2 classes
```

## Slide 7-A. TCN Model Structure 상세

Best live model은 오른팔 pose sequence를 직접 입력받는 causal residual TCN이다.

End-to-end 구조:

```text
raw handmark CSV / stdin stream
  -> right shoulder / right elbow / right wrist
  -> H36M17 right-arm masked pose
  -> sliding window [B, 45, 17, 3]
  -> select right-arm joints [14, 15, 16]
  -> flatten joint channels
  -> TCN input [B, 9, 45]
  -> input mean/std normalization
  -> causal residual Conv1d TCN
  -> temporal mean pooling
  -> tempo head + gain head
  -> LiveSmoother
  -> MIDI tempo / velocity / CC11
```

Input tensor:

```text
pose window: [B, T, 17, 3]
T = 45 frames ~= 3.0s at 15fps
right_arm_indices = [14, 15, 16]
channels per joint = x, y, confidence

selected right arm: [B, 45, 3, 3]
TCN input: [B, 9, 45]
9 channels = 3 joints x 3 values
```

TCN encoder:

```text
input_channels = 9
hidden_channels = 64
levels = 4
kernel_size = 5
dropout = 0.1
dilations = 1, 2, 4, 8
```

각 temporal block:

```text
Conv1d(in_channels, hidden_channels, kernel=5, dilation=d)
  -> causal chomp
  -> ReLU
  -> Dropout(0.1)
  -> Conv1d(hidden_channels, hidden_channels, kernel=5, dilation=d)
  -> causal chomp
  -> ReLU
  -> Dropout(0.1)
  -> residual connection
  -> ReLU
```

Residual path:

```text
if input_channels != hidden_channels:
  1x1 Conv1d projection
else:
  identity
```

Classifier heads:

```text
encoded: [B, 64, 45]
pooled = mean(encoded, time)  # [B, 64]
pooled = LayerNorm(64)

tempo_head: Linear(64, 4)
gain_head: Linear(64, 2)
```

출력 의미:

```text
tempo logits:
  class 0 -> 60 BPM
  class 1 -> 80 BPM
  class 2 -> 100 BPM
  class 3 -> 120 BPM

gain logits:
  class 0 -> small -> dynamics 0.25
  class 1 -> large -> dynamics 0.85
```

Live smoothing policy:

```text
switch_threshold: 0.58
fast_switch_threshold: 0.78
confirm_updates: 2
update interval: 3 frames ~= 0.2s
```

모델 설계 의도:

- causal Conv1d로 현재/과거 window만 사용해 live stream에 맞춘다.
- dilation `1,2,4,8`로 3초 window 안의 short-term beat pattern과 slower tempo pattern을 같이 본다.
- residual block으로 작은 데이터에서도 안정적으로 학습한다.
- tempo와 gain을 multi-task로 같이 학습해 같은 오른팔 motion에서 속도와 강도를 동시에 분리한다.
- 최종 MIDI 출력은 raw prediction을 바로 쓰지 않고 smoother를 거쳐 false switch를 줄인다.

## Slide 8. 학습 Config

```text
model_type: causal_tcn_right_arm_pose
input_channels: 9
hidden_channels: 64
levels: 4
kernel_size: 5
dropout: 0.1
epochs: 45
batch_size: 256
optimizer: AdamW
lr: 0.001
weight_decay: 0.0001
loss: CE(tempo) + 0.5 * CE(gain)
```

학습 데이터:

```text
train_sessions: 11
train_samples: 2247
tempo bins: 60 / 80 / 100 / 120
gain classes: small / large
```

## Slide 9. Model Score

최신 supplied-set rerun 결과:

```text
discovered raw CSV files: 15
eval sessions: 11
sample count after 3s transition margin: 1824
```

| Metric | Score |
|---|---:|
| Tempo accuracy | 1.0000 |
| Gain accuracy | 1.0000 |
| 80 BPM recall | 1.0000 |
| 100 BPM recall | 1.0000 |
| 120 BPM recall | 1.0000 |
| BPM MAE | 0.0000 |
| False switches / min | 0.0000 |
| Missed switch count | 0 |
| Switch delay p90 | 0.0000 s |

## Slide 10. Runtime Score

실시간성 결과:

| Metric | Value |
|---|---:|
| p90 inference/update | 1.9984 ms |
| p95 inference/update | 2.0884 ms |
| max inference/update | 2.3526 ms |
| update budget | 200 ms |
| headroom | 100.08x |
| stream contract errors | 0 |
| readiness | GO |

해석:

```text
실시간 MIDI 제어에는 충분한 latency margin을 확보했다.
```

## Slide 11. MotionBERT 후보 결과

비교 후보:

```text
MotionBERT-Lite frozen encoder
+ MLP conducting head
```

Best MotionBERT candidate:

```text
window: 45 frames
epochs: 240
hidden_dim: 512
lr: 0.003
dropout: 0.1
```

Score:

| Metric | Score |
|---|---:|
| Transition tempo acc | 0.9989 |
| Gain acc | 1.0000 |
| 80 BPM recall | 0.9953 |
| 100 BPM recall | 1.0000 |
| 120 BPM recall | 1.0000 |
| BPM MAE | 0.0226 |
| False switches / min | 0.0000 |

정리:

```text
MotionBERT도 가능성은 높았지만,
현재 live-facing best는 더 빠르고 단순한 TCN이다.
```

## Slide 12. 현재 한계와 다음 단계

현재 claim:

```text
fixed-camera supplied-set live pilot: GO
```

아직 claim 불가:

```text
strict independent heldout generalization
```

부족한 heldout root:

```text
dataset/strict_heldout_static_v1
dataset/strict_heldout_transitions_v1
```

다음 단계:

- 독립 static heldout 수집
- 독립 transition heldout 수집
- train/eval root 완전 분리
- strict post-arrival chain 재실행
- generalization score 보고

## Slide 13. 발표용 결론

```text
본 실험은 오른손 지휘 pose만으로 MIDI tempo와 dynamics를
실시간 제어할 수 있음을 fixed-camera live pilot 조건에서 확인했다.

Annotation은 녹화 protocol 기반 자동 labeling으로 구성했고,
transition boundary window를 mixed label로 분리해 label noise를 줄였다.

최신 best live model은 45-frame causal TCN이며,
supplied-set 기준 tempo/gain accuracy 1.0,
p90 latency 약 2ms로 실시간 제어 조건을 만족했다.

다만 strict independent heldout은 아직 수집 전이므로,
현재 결과는 일반화 완료가 아니라 live pilot feasibility 결과로 해석한다.
```

## References

```text
scores: docs/exp/right_hand_conducting_scores.md
model card: docs/exp/right_hand_conducting_model_card.md
handoff runbook: docs/exp/tcn_live_handoff_runbook.md
latest TCN report: docs/exp/goal_reports/2026-06-17_117_full_test_release_and_status_rerun.md
handoff refresh report: docs/exp/goal_reports/2026-06-17_119_tcn_handoff_and_model_card_refresh.md
TCN bundle: outputs/right_conducting/selected_tcn_handmark_live45f
TCN score: outputs/right_conducting/tcn_alltest_latest/stream_set_score_fulltest_latest.json
TCN current status: outputs/right_conducting/tcn_alltest_latest/current_status_fulltest_latest.json
TCN readiness: outputs/right_conducting/tcn_alltest_latest/stream_readiness.json
```
