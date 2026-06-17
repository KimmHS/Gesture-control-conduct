# Right-Arm Conducting Recording Plan

이 문서는 right-arm-only conducting model용 recording 계획의 현재 확정본이다.

## v0 Training Dataset

v0 training target은 `60 / 80 / 100 / 120 BPM`만 사용한다.
`140 / 160 BPM`은 v0에서 제외한다.

조건:

```text
duration: 60초
meter: 2박 / 3박 / 4박
dynamics: large / small
audio: 기본 OFF
output: data/recordings
```

현재 완료:

```text
target takes: 24
completed takes: 24
frames: 25394
120-frame windows: 3773  # about 8s windows at current ~15fps; count kept for old artifacts
```

체크리스트:

```text
docs/RECORDING_CHECKLIST.md
docs/recording_checklist_interactive.html
```

주의:

```text
session_20260616_212313_bpm120_beat2_small
```

이 세션은 중간에 노이즈가 낀 구간이 있으므로 학습 전 확인 또는 trim이 필요하다.

## Evaluation Dataset

Evaluation set은 training set과 섞지 않고 `data/evaluation`에 저장한다.
한 번에 하나의 변수만 바뀌게 측정한다.

baseline:

```text
100 BPM / 4박 / large / 60초
```

변수별 평가:

```text
dynamics only: 100 BPM / 4박 / small
beat only:     100 BPM / 2박 / large, 100 BPM / 3박 / large
tempo only:    60 BPM / 4박 / large, 120 BPM / 4박 / large
```

총량:

```text
6 takes x 60초 = 6분
```

체크리스트:

```text
docs/EVALUATION_RECORDING_CHECKLIST.md
```

## Dataset Policy

Training에는 augmentation을 적용할 수 있다.
Evaluation/test에는 augmentation을 적용하지 않는다.

```text
train: original + augmentation
evaluation: original only
test: original only
```
