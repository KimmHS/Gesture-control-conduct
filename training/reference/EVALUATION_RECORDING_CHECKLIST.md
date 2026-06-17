# Evaluation Recording Checklist

Evaluation set은 training set과 섞지 않는다. 모든 take는 `60초` 기준이고 `data/evaluation`에 저장한다.

원칙:

```text
한 번에 하나의 변수만 바꾼다.
baseline: 100 BPM / 4박 / large
audio: 기본 OFF
augmentation: evaluation/test에는 적용하지 않음
```

실행 후 프로그램 창에서 `R`을 눌러 녹화를 시작한다.

---

## v0 Evaluation Set

### Baseline

- [ ] 100 BPM / 4박 / large / 60초

```bash
cd /Users/jongha/vscode/Gesture-control-conduct && conda activate asr && python record_data.py --bpm 100 --meter 4 --dynamics-condition large --target-seconds 60 --output-root data/evaluation
```

### Dynamics Only

baseline에서 dynamics만 바꾼다.

- [ ] 100 BPM / 4박 / small / 60초

```bash
cd /Users/jongha/vscode/Gesture-control-conduct && conda activate asr && python record_data.py --bpm 100 --meter 4 --dynamics-condition small --target-seconds 60 --output-root data/evaluation
```

### Beat Only

baseline에서 박자만 바꾼다. BPM과 dynamics는 고정한다.

- [ ] 100 BPM / 2박 / large / 60초

```bash
cd /Users/jongha/vscode/Gesture-control-conduct && conda activate asr && python record_data.py --bpm 100 --meter 2 --dynamics-condition large --target-seconds 60 --output-root data/evaluation
```

- [ ] 100 BPM / 3박 / large / 60초

```bash
cd /Users/jongha/vscode/Gesture-control-conduct && conda activate asr && python record_data.py --bpm 100 --meter 3 --dynamics-condition large --target-seconds 60 --output-root data/evaluation
```

### Tempo Only

baseline에서 BPM만 바꾼다. 박자와 dynamics는 고정한다.

- [ ] 60 BPM / 4박 / large / 60초

```bash
cd /Users/jongha/vscode/Gesture-control-conduct && conda activate asr && python record_data.py --bpm 60 --meter 4 --dynamics-condition large --target-seconds 60 --output-root data/evaluation
```

- [ ] 120 BPM / 4박 / large / 60초

```bash
cd /Users/jongha/vscode/Gesture-control-conduct && conda activate asr && python record_data.py --bpm 120 --meter 4 --dynamics-condition large --target-seconds 60 --output-root data/evaluation
```

---

## Summary

```text
total: 6 takes
duration: 6분
variables:
  dynamics: large <-> small
  beat: 2박 / 3박 / 4박
  tempo: 60 / 100 / 120 BPM
```
