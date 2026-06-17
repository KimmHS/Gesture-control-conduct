# Right Conducting Final Summary

## 결론

- 최종 후보는 `24f / 1.6s`, stride `3f / 0.2s`, transition boundary margin `+/-0.5s` 기준으로 정리했다.
- `2초는 길다`는 조건을 반영하면 `24f / 1.6s`가 가장 현실적인 short-window 후보다.
- MotionBERT는 backbone을 고정하고 conducting head만 학습한 결과라 switching/tempo task에는 한계가 크다.
- TCN은 현재 데이터에 맞춰 end-to-end로 학습되어 switching은 훨씬 안정적이지만, 결과 범위는 quick-probe라 heldout 검증이 필요하다.
- Gain 성능은 병목이 아니다. 병목은 tempo switching, 특히 transition 주변 흔들림과 strict 222455의 120 BPM recall이다.

## Challenge: Tempo Switching 구간 문제

### 문제 상황

- Dataset에서 tempo가 switching 되는 구간에서 성능 저하가 발생했다.
- 특히 transition 이후 짧게 남는 `80 BPM tail`을 모델이 놓치는 현상이 있었다.
- 사람이 실제로 tempo를 바꾸는 순간과 label boundary는 정확히 한 프레임으로 떨어지지 않는다.
- 따라서 transition 직전/직후 window에는 이전 tempo와 다음 tempo의 motion이 섞일 수 있다.
- 이 구간을 그대로 학습시키면 모델 입장에서는 같은 pose 흐름에 서로 다른 label이 붙는 것처럼 보일 수 있다.

### 구체적으로 발생한 문제

- Raw prediction이 transition 주변에서 `80 -> 120`, `120 -> 80` 사이를 흔들었다.
- 전환 직후 80 BPM 구간이 짧거나 motion amplitude가 작으면, 모델이 이를 안정적인 80 BPM으로 보지 못하고 이전/다음 tempo로 끌려가는 케이스가 있었다.
- MotionBERT head-only 방식에서는 이 문제가 더 크게 나타났다.
  - Backbone은 frozen이라 conducting tempo switching에 맞게 feature가 조정되지 않았다.
  - right-arm representation을 `mean/std/delta`로 pooling하면서 beat phase와 transition timing 정보가 압축됐다.
  - 결과적으로 broader devset에서는 어느 정도 맞지만, strict 222455에서는 120 BPM recall이 거의 0에 가까워지는 failure가 있었다.
- Gain은 높은 성능을 유지했으므로, 핵심 병목은 gain이 아니라 tempo transition 안정성이었다.

### 해결 방향

- Label boundary 정책을 명확히 했다.
  - 사람이 바꾸는 순간과 label boundary가 총 `1초` 정도 흔들릴 수 있다고 보고, transition 기준 `+/-0.5s` margin을 적용했다.
  - 학습에서는 transition `+/-0.5s`와 겹치는 window를 제거했다.
  - 평가에서도 `devset@0.5` 기준으로 transition 주변 애매한 샘플을 제외하고 성능을 봤다.
- Window 길이를 다시 sweep했다.
  - `2초`는 길다는 판단에 따라 `0.6s, 0.8s, 1.0s, 1.2s, 1.6s` window를 추가 실험했다.
  - under-2s 조건에서는 `24f / 1.6s`가 가장 안정적인 후보였다.
- Smoothing을 적용해 live output의 불필요한 switch를 줄였다.
  - MotionBERT 24f false/min: `19.69 -> 5.98`
  - TCN 24f false/min: `1.35 -> 0.00`
  - 단, MotionBERT는 smoothing 후 delay p90이 `0.330s -> 0.736s`로 늘어나는 tradeoff가 있었다.
- 모델 구조 관점에서는 TCN이 더 적합하게 보였다.
  - TCN은 right-arm pose sequence를 직접 temporal conv로 학습하므로 transition pattern을 더 직접적으로 학습했다.
  - MotionBERT는 frozen backbone + shallow head라 transition-specific feature adaptation이 부족했다.

### 현재 결론

- Transition 주변 문제는 단순 accuracy 문제가 아니라 boundary policy, window length, smoothing policy가 같이 걸린 문제다.
- 현재 short-window 후보는 `24f / 1.6s`가 가장 현실적이다.
- MotionBERT는 head-only 결과로는 한계가 있으므로, 다음 단계에서는 backbone fine-tuning 또는 last-N-layer unfreeze가 필요하다.
- TCN은 switching 안정성은 좋지만 quick-probe 결과이므로 heldout transition set에서 재검증해야 한다.

## 모델 저장 위치

- Bundle root: `/home/jhkim/jongha/Gesture-control-conduct/training/right_conducting_boundary0p5_24f_20260617`
- MotionBERT head: `right_conducting_boundary0p5_24f_20260617/motionbert_24f/all_train_head.pt`
- MotionBERT backbone config: `right_conducting_boundary0p5_24f_20260617/motionbert_24f/MB_lite.yaml`
- MotionBERT backbone checkpoint: `right_conducting_boundary0p5_24f_20260617/motionbert_24f/mb_lite_v0.pt`
- TCN checkpoint: `right_conducting_boundary0p5_24f_20260617/tcn_24f/tcn_conducting_head.pt`
- Bundle manifest: `right_conducting_boundary0p5_24f_20260617/bundle_manifest.json`

## 학습 방식

### MotionBERT

- MotionBERT는 **head만 학습**했다.
- `mb_lite_v0.pt` backbone은 frozen feature extractor로 사용했다.
- 저장된 `all_train_head.pt`는 backbone이 아니라 conducting head weights다.
- 구조적으로는 `MotionBERT backbone + trained conducting head`를 같이 로드해야 한다.
- feature mode는 `mean_std_delta`, input mask mode는 `as_is`, normalization은 `camera`다.
- 현재 run에서 실제 head 학습에 사용된 augmentation count는 `0`이다. Dataset prep에는 augmentation recipe가 준비되어 있었지만, cached feature head 학습은 original windows만 사용했다.

### TCN

- TCN은 right-arm pose 입력으로 모델 전체를 학습했다.
- 입력은 right shoulder/elbow/wrist의 x/y/confidence를 flatten한 `[B, 9, T]` 형태다.
- train-set mean/std로 channel-wise normalization을 적용했고, checkpoint 안에 `input_mean`, `input_std`, `config`, `model_state`가 같이 저장되어 있다.
- synthetic augmentation은 사용하지 않았다.

## MotionBERT, TCN 모델 구조 요약

### MotionBERT

- 입력: window pose sequence `[T, 17, 3]`.
- Backbone: `MB_lite` MotionBERT checkpoint를 frozen feature extractor로 사용.
- Feature 추출: backbone representation에서 right arm joint만 사용한다.
  - right shoulder
  - right elbow
  - right wrist
- Pooling/summary: right-arm representation을 `mean_std_delta`로 압축한다.
  - mean
  - std
  - abs temporal delta mean
  - abs temporal delta std
- 최종 cached feature shape: 24f 기준 `[10640, 2048]`.
- 학습된 부분: MotionBERT backbone이 아니라 conducting head만 학습했다.
- Head 구조:
  - `LayerNorm`
  - `Linear`
  - `GELU`
  - `Dropout`
  - output heads
- Output heads:
  - tempo class head: 4-class, `[60, 80, 100, 120]`
  - BPM distribution head: 4-bin soft distribution
  - gain head: 2-class, `small / large`
  - dynamics head: scalar dynamics value

요약하면 MotionBERT는 `frozen backbone + right-arm pooled feature + shallow conducting head` 구조다. Backbone을 conducting task에 맞게 fine-tuning하지 않았기 때문에 switching/tempo phase 정보가 충분히 살아있지 않을 수 있다.

### TCN

- 입력: right-arm pose window `[B, 9, T]`.
  - 3 joints: right shoulder, right elbow, right wrist
  - each joint: x, y, confidence
  - 총 9 channels
- Normalization: train-set 기준 channel-wise mean/std normalization.
- Encoder: residual causal TCN.
  - hidden channels: 64
  - levels: 4
  - kernel size: 5
  - dilation: `1, 2, 4, 8`
  - dropout: 0.1
- Temporal handling:
  - trailing window만 사용한다.
  - future frame은 보지 않는다.
  - Conv1d padding 후 chomp로 causal alignment를 유지한다.
- Pooling: encoded sequence를 time dimension 평균 pooling.
- Head:
  - `LayerNorm`
  - tempo linear head
  - gain linear head
- Output heads:
  - tempo class head: 4-class, `[60, 80, 100, 120]`
  - gain head: 2-class, `small / large`

요약하면 TCN은 `right-arm pose -> temporal conv encoder -> mean pooling -> tempo/gain heads` 구조이며, 이번 데이터에서 모델 전체를 직접 학습했다. 그래서 frozen MotionBERT head 방식보다 transition switching에 더 직접적으로 맞춰졌다.

## Boundary / Window 정책

- 사람의 실제 switch 순간과 label boundary는 총 `1초` 정도 흔들릴 수 있다고 보고, transition 기준 `+/-0.5s`를 margin으로 잡았다.
- 학습에서는 transition `+/-0.5s`와 겹치는 window를 제거했다.
- 평가에서도 `devset@0.5`는 transition `+/-0.5s` 샘플을 제외하고 계산했다.
- live 정책은 trailing window이며 future frame은 사용하지 않는다.
- `24f / 1.6s`는 예측 시점 이전 1.6초를 보고 window 끝 timestamp를 현재 예측으로 낸다.

## 핵심 성능표

### MotionBERT

| window | sec | CV tempo | CV gain | devset@0.5 tempo | devset@0.5 gain | precision | recall | f1 score | r80 | r120 | false/min |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 9f | 0.6 | 0.6166 | 0.9421 | 0.7510 | 0.9919 | 0.5433 | 0.5352 | 0.5375 | 0.6183 | 0.8811 | 9.44 |
| 12f | 0.8 | 0.6406 | 0.9541 | 0.7673 | 0.9979 | 0.5531 | 0.5324 | 0.5392 | 0.6320 | 0.9383 | 8.15 |
| 15f | 1.0 | 0.6443 | 0.9689 | 0.7993 | 0.9979 | 0.7713 | 0.7551 | 0.7580 | 0.6308 | 0.9573 | 9.33 |
| 18f | 1.2 | 0.6530 | 0.9804 | 0.8266 | 0.9986 | 0.6046 | 0.5961 | 0.5979 | 0.7076 | 0.9394 | 8.03 |
| 24f | 1.6 | 0.7068 | 0.9789 | 0.8947 | 0.9985 | 0.8748 | 0.8593 | 0.8659 | 0.8986 | 0.9643 | 5.98 |
| 30f | 2.0 | 0.7149 | 0.9907 | 0.9011 | 1.0000 | 0.6594 | 0.6677 | 0.6628 | 0.9452 | 0.9051 | 4.09 |
| 45f | 3.0 | 0.7545 | 0.9975 | 0.9659 | 1.0000 | 0.9562 | 0.9606 | 0.9571 | 0.9065 | 1.0000 | 1.20 |
| 60f | 4.0 | 0.7389 | 0.9974 | 0.9289 | 1.0000 | 0.9219 | 0.9101 | 0.9131 | 0.8429 | 1.0000 | 3.27 |
| 90f | 6.0 | 0.7466 | 0.9981 | 0.9770 | 1.0000 | 0.9714 | 0.9677 | 0.9691 | 0.9964 | 0.9890 | 0.64 |
| 120f | 8.0 | 0.7111 | 1.0000 | 0.9887 | 1.0000 | 0.9822 | 0.9899 | 0.9858 | 0.9810 | 0.9887 | 0.00 |

### TCN Quick-Probe

| window | sec | CV tempo | CV gain | devset@0.5 tempo | devset@0.5 gain | precision | recall | f1 score | r80 | r120 | false/min |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 9f | 0.6 | - | - | 0.9466 | 0.9996 | 0.9245 | 0.9430 | 0.9332 | 0.9479 | 0.9502 | 27.72 |
| 12f | 0.8 | - | - | 0.9501 | 0.9996 | 0.9131 | 0.9696 | 0.9373 | 0.9185 | 0.9972 | 29.17 |
| 15f | 1.0 | - | - | 0.9876 | 1.0000 | 0.9804 | 0.9866 | 0.9835 | 0.9854 | 0.9957 | 6.66 |
| 18f | 1.2 | - | - | 0.9979 | 1.0000 | 0.9986 | 0.9950 | 0.9968 | 0.9993 | 1.0000 | 1.34 |
| 24f | 1.6 | - | - | 0.9996 | 1.0000 | 0.9998 | 0.9995 | 0.9996 | 1.0000 | 0.9985 | 0.00 |
| 30f | 2.0 | - | - | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.00 |
| 45f | 3.0 | - | - | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.00 |
| 60f | 4.0 | - | - | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.00 |
| 90f | 6.0 | - | - | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.00 |
| 120f | 8.0 | - | - | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.00 |

## 24f 추천 후보 비교

| model | window | tempo | gain | precision | recall | f1 | r80 | r120 | false/min | note |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| MotionBERT | 24f / 1.6s | 0.8947 | 0.9985 | 0.8748 | 0.8593 | 0.8659 | 0.8986 | 0.9643 | 5.98 | head-only, strict gate NO_GO |
| TCN quick-probe | 24f / 1.6s | 0.9996 | 1.0000 | 0.9998 | 0.9995 | 0.9996 | 1.0000 | 0.9985 | 0.00 | same-root quick-probe, heldout 필요 |

## Smoothing / Delay

- Smoothing은 raw prediction 이후 live output 안정화를 위해 적용했다.
- 정책: `switch_threshold=0.58`, `fast_switch_threshold=0.78`, `confirm_updates=2`, BPM EMA `alpha=0.15`, dynamics EMA `alpha=0.10`.
- 구조적 지연은 `24f / 1.6s` trailing window가 가장 큰 요인이고, update interval은 `0.2s`다.
- smoothing은 보통 candidate switch 확인에 약 한 update step, 즉 `~0.2s`를 추가할 수 있다. confidence가 높으면 fast switch로 바로 바뀐다.

| model | raw false/min | smoothed false/min | improvement | raw delay p90 | smoothed delay p90 |
|---|---:|---:|---:|---:|---:|
| MotionBERT 24f | 19.69 | 5.98 | 69.6% lower | 0.330s | 0.736s |
| TCN quick-probe 24f | 1.35 | 0.00 | 100.0% lower | 0.000s | 0.000s |

## 왜 MotionBERT 성능이 약한가

- 현재 MotionBERT는 conducting task로 backbone fine-tuning을 하지 않았다.
- frozen representation을 window-level mean/std/delta로 pooling해서 쓰기 때문에 beat phase와 switch 순간 정보가 압축된다.
- 현재 head 학습에는 실제 pose-level augmentation이 적용되지 않았다.
- 그래서 broader devset에서는 어느 정도 성능이 나오지만, strict 222455 같은 다른 분포에서는 120 BPM recall이 거의 0에 가깝게 무너진다.
- 이 결과는 “MotionBERT 자체가 안 된다”보다는 “frozen feature + shallow head 방식으로는 이 task에 부족하다”로 해석하는 게 맞다.

## 다음 실험 제안

- MotionBERT full fine-tuning 또는 last N layers unfreeze.
- LR 분리: head `1e-3`, backbone `1e-5 ~ 3e-5`.
- pose-level augmentation을 실제 입력에 적용: jitter, dropout, affine, time stretch, amplitude scaling.
- `24f`와 `30f` 중심으로 재학습.
- strict 222455는 단일 gate가 아니라 failure-case 분석 세트로 분리해서 보는 것이 적절하다.
- TCN은 heldout transition set으로 다시 검증해야 한다. 현재 수치는 quick-probe라 과대평가 가능성이 있다.

## 관련 보고서

- `right_conducting_boundary0p5_24f_20260617/reports/boundary0p5_compact_table.md`
- `right_conducting_boundary0p5_24f_20260617/reports/boundary0p5_metric_cards.md`
- `right_conducting_boundary0p5_24f_20260617/reports/augmentation_delay_smoothing_summary.md`
- `right_conducting_boundary0p5_24f_20260617/reports/boundary0p5_all_windows_tcn_motionbert_summary.md`
