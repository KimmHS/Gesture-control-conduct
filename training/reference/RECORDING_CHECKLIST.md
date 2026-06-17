# Recording Checklist

최종 training recording 체크리스트다. 모든 take는 `60초` 기준이다.

VSCode에서 클릭 가능한 체크리스트는 [`recording_checklist_interactive.html`](recording_checklist_interactive.html)을 사용한다.
각 항목에는 터미널에 바로 붙여넣을 수 있는 실행 command와 `Copy` 버튼이 붙어 있다.

실행 command 예시:

```bash
cd /Users/jongha/vscode/Gesture-control-conduct && conda activate asr && python record_data.py --bpm 60 --meter 2 --dynamics-condition small --target-seconds 60
```

프로그램이 뜨면 `R`을 눌러 녹화를 시작한다. 메트로놈 소리는 기본 OFF다.

---

## Final Recording Matrix

### 60 BPM

- [x] 60 BPM / 2박 / large / 60초 - session_20260616_174336_bpm060_beat2_large
- [x] 60 BPM / 3박 / large / 60초 - session_20260616_174510_bpm060_beat3_large
- [x] 60 BPM / 4박 / large / 60초 - session_20260616_174636_bpm060_beat4_large
- [x] 60 BPM / 2박 / small / 60초 - session_20260616_180022_bpm060_beat2_small
- [x] 60 BPM / 3박 / small / 60초 - session_20260616_180143_bpm060_beat3_small
- [x] 60 BPM / 4박 / small / 60초 - session_20260616_210424_bpm060_beat4_small

### 80 BPM

- [x] 80 BPM / 2박 / large / 60초 - session_20260616_210646_bpm080_beat2_large
- [x] 80 BPM / 3박 / large / 60초 - session_20260616_210816_bpm080_beat3_large
- [x] 80 BPM / 4박 / large / 60초 - session_20260616_210936_bpm080_beat4_large
- [x] 80 BPM / 2박 / small / 60초 - session_20260616_211053_bpm080_beat2_small
- [x] 80 BPM / 3박 / small / 60초 - session_20260616_211208_bpm080_beat3_small
- [x] 80 BPM / 4박 / small / 60초 - session_20260616_211325_bpm080_beat4_small

### 100 BPM

- [x] 100 BPM / 2박 / large / 60초 - session_20260616_211510_bpm100_beat2_large
- [x] 100 BPM / 3박 / large / 60초 - session_20260616_211632_bpm100_beat3_large
- [x] 100 BPM / 4박 / large / 60초 - session_20260616_211753_bpm100_beat4_large
- [x] 100 BPM / 2박 / small / 60초 - session_20260616_211918_bpm100_beat2_small
- [x] 100 BPM / 3박 / small / 60초 - session_20260616_212033_bpm100_beat3_small
- [x] 100 BPM / 4박 / small / 60초 - session_20260616_212150_bpm100_beat4_small

### 120 BPM

- [x] 120 BPM / 2박 / large / 60초 - session_20260616_003523_bpm120_beat2
- [x] 120 BPM / 3박 / large / 60초 - session_20260616_005237_bpm120_beat3
- [x] 120 BPM / 4박 / large / 60초 - session_20260616_005614_bpm120_beat4
- [x] 120 BPM / 2박 / small / 60초 - session_20260616_212313_bpm120_beat2_small, 중간 노이즈 주의
- [x] 120 BPM / 3박 / small / 60초 - session_20260616_213424_bpm120_beat3_small
- [x] 120 BPM / 4박 / small / 60초 - session_20260616_213543_bpm120_beat4_small

## Excluded From v0

140 BPM과 160 BPM은 v0 training target에서 제외한다.

촬영 합계:

```text
v0 목표: 24 takes
완료: 24 takes
남은 촬영: 0 takes
현재 frames: 25394
현재 120-frame windows: 3773  # 현재 ~15fps 기준 약 8초 window; 기존 산출물 참고용
```

---

## Evaluation Set

평가용 recording은 [`EVALUATION_RECORDING_CHECKLIST.md`](EVALUATION_RECORDING_CHECKLIST.md)에 따로 둔다.
Evaluation set은 training set과 섞지 않고 `data/evaluation`에 저장한다.
