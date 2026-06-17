구현 내용 및 결과

## Task 설명

lightweight Gesture-Based MIDI Performance Control and Orchestration

## Demo

영상과 함께

#### spec

`HandTracker`는 MediaPipe HandLandmarker를 사용

cam 1280×720, 15 frame

## Method

#### Tempo, Dynamics

#### rule-base :

Tempo는 **오른손 손목의 최근 이동량**으로 계산

최근 window 안의 손목 좌표들을 가져옴\
→ 연속 프레임 간 거리 합산\
→ motion_energy_px 계산\
→ floor~ceiling 사이로 normalize\
→ min_rate~max_rate로 mapping\
→ smoothing 적용\
→ playback_rate로 반영

Dynamics는 **최근 손목 이동 범위 span**으로 계산

최근 window 안의 손목 좌표들을 가져옴\
→ x 범위, y 범위 계산\
→ sqrt(width² + height²) = span_px\
→ reference_span_px로 normalize\
→ min_volume~max_volume로 mapping\
→ smoothing 적용

#### deep-learning :

손목, 팔꿈치, 어깨, 일부 손 좌표

TCN based model

Motionbert + linear head

#### dataset

수집 환경 macbook air m3

#### tempo/gain Fixed set

1분씩 , 총 1시간

tempo : 60 / 80 / 100 / 120 BPM

gain : small, large

#### Conversion Set

47초씩 총 약 20분

15초 - 1초 - 15초 - 1초 - 15초

15초동안 single set 지속

1초동안 transition

#### evaluation set

* 자유롭게 5초~10초마다 요소를 변경.

* 약 1분 구성

* 5명 5개씩

annotation

#### model structure

TCN

Motionbert : 2D Skeletons 를 입력으로 받아서 pose estimate , action recognition, … 진행 하는 모델

#### challenge

dataset 에서 tempo 가 switching 되는 부분에서 문제 발생

* transition 이후 80 BPM tail을 놓치는 현상이 있었다.

* 구체적으로 어떤 문제?

* 어떻게 해결?

## Result

#### Metric

TCN

Motionbert

acc

precision

recall

f1 score

실시간성

| Metric               | Value     |
| -------------------- | --------- |
| p90 inference/update | 1.9984 ms |
| p95 inference/update | 2.0884 ms |
| max inference/update | 2.3526 ms |
| update budget        | 200 ms    |
| headroom             | 100.08x   |

#### Table

## MotionBERT

| window | sec | CV tempo | CV gain | devset@0.5 tempo | devset@0.5 gain | precision | recall | f1 score | r80    | r120   | false/min |
| ------ | --- | -------- | ------- | ---------------- | --------------- | --------- | ------ | -------- | ------ | ------ | --------- |
| 9f     | 0.6 | 0.6166   | 0.9421  | 0.7510           | 0.9919          | 0.5433    | 0.5352 | 0.5375   | 0.6183 | 0.8811 | 9.44      |
| 12f    | 0.8 | 0.6406   | 0.9541  | 0.7673           | 0.9979          | 0.5531    | 0.5324 | 0.5392   | 0.6320 | 0.9383 | 8.15      |
| 15f    | 1.0 | 0.6443   | 0.9689  | 0.7993           | 0.9979          | 0.7713    | 0.7551 | 0.7580   | 0.6308 | 0.9573 | 9.33      |
| 18f    | 1.2 | 0.6530   | 0.9804  | 0.8266           | 0.9986          | 0.6046    | 0.5961 | 0.5979   | 0.7076 | 0.9394 | 8.03      |
| 24f    | 1.6 | 0.7068   | 0.9789  | 0.8947           | 0.9985          | 0.8748    | 0.8593 | 0.8659   | 0.8986 | 0.9643 | 5.98      |
| 30f    | 2.0 | 0.7149   | 0.9907  | 0.9011           | 1.0000          | 0.6594    | 0.6677 | 0.6628   | 0.9452 | 0.9051 | 4.09      |
| 45f    | 3.0 | 0.7545   | 0.9975  | 0.9659           | 1.0000          | 0.9562    | 0.9606 | 0.9571   | 0.9065 | 1.0000 | 1.20      |
| 60f    | 4.0 | 0.7389   | 0.9974  | 0.9289           | 1.0000          | 0.9219    | 0.9101 | 0.9131   | 0.8429 | 1.0000 | 3.27      |
| 90f    | 6.0 | 0.7466   | 0.9981  | 0.9770           | 1.0000          | 0.9714    | 0.9677 | 0.9691   | 0.9964 | 0.9890 | 0.64      |
| 120f   | 8.0 | 0.7111   | 1.0000  | 0.9887           | 1.0000          | 0.9822    | 0.9899 | 0.9858   | 0.9810 | 0.9887 | 0.00      |

## TCN Quick-Probe

| window | sec | CV tempo | CV gain | devset@0.5 tempo | devset@0.5 gain | precision | recall | f1 score | r80    | r120   | false/min |
| ------ | --- | -------- | ------- | ---------------- | --------------- | --------- | ------ | -------- | ------ | ------ | --------- |
| 9f     | 0.6 | -        | -       | 0.9466           | 0.9996          | 0.9245    | 0.9430 | 0.9332   | 0.9479 | 0.9502 | 27.72     |
| 12f    | 0.8 | -        | -       | 0.9501           | 0.9996          | 0.9131    | 0.9696 | 0.9373   | 0.9185 | 0.9972 | 29.17     |
| 15f    | 1.0 | -        | -       | 0.9876           | 1.0000          | 0.9804    | 0.9866 | 0.9835   | 0.9854 | 0.9957 | 6.66      |
| 18f    | 1.2 | -        | -       | 0.9979           | 1.0000          | 0.9986    | 0.9950 | 0.9968   | 0.9993 | 1.0000 | 1.34      |
| 24f    | 1.6 | -        | -       | 0.9996           | 1.0000          | 0.9998    | 0.9995 | 0.9996   | 1.0000 | 0.9985 | 0.00      |
| 30f    | 2.0 | -        | -       | 1.0000           | 1.0000          | 1.0000    | 1.0000 | 1.0000   | 1.0000 | 1.0000 | 0.00      |
| 45f    | 3.0 | -        | -       | 1.0000           | 1.0000          | 1.0000    | 1.0000 | 1.0000   | 1.0000 | 1.0000 | 0.00      |
| 60f    | 4.0 | -        | -       | 1.0000           | 1.0000          | 1.0000    | 1.0000 | 1.0000   | 1.0000 | 1.0000 | 0.00      |
| 90f    | 6.0 | -        | -       | 1.0000           | 1.0000          | 1.0000    | 1.0000 | 1.0000   | 1.0000 | 1.0000 | 0.00      |
| 120f   | 8.0 | -        | -       | 1.0000           | 1.0000          | 1.0000    | 1.0000 | 1.0000   | 1.0000 | 1.0000 | 0.00      |

## Column Guide

* `window`: prediction window size in frames.

* `sec`: approximate window length in seconds at 15 fps.

* `CV tempo`: cross-validation tempo accuracy.

* `CV gain`: cross-validation gain accuracy.

* `devset@0.5 tempo`: tempo accuracy after excluding transition +/-0.5s samples.

* `devset@0.5 gain`: gain accuracy after excluding transition +/-0.5s samples.

* `precision`: tempo macro precision at margin 0.5s.

* `recall`: tempo macro recall at margin 0.5s.

* `f1 score`: tempo macro F1 at margin 0.5s.

* `r80`: 80 BPM recall at margin 0.5s.

* `r120`: 120 BPM recall at margin 0.5s.

* `false/min`: smoothed false tempo switches per minute.
