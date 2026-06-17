# Current Recording Data

현재 active v0 training recording 요약이다.

Active paths:

```text
train dataset:
  dataset/recordings.zip
  dataset/recordings
  outputs/right_conducting/recordings_staged_current.zip  # canonical staged smoke artifact

heldout eval dataset:
  dataset/evaluation_transitions/session_20260616_222455_eval
  dataset/evaluation_transitions/session_20260616_215630_eval  # relabel 전 score 제외
```

주의:

- v0 training 기준은 `60초`이다.
- 140 BPM과 160 BPM은 v0 target에서 제외했다.
- 현재 데이터는 약 15fps이므로 `60-frame window ~= 4초`, `120-frame window ~= 8초`이다. 아래 `120-frame windows` 컬럼은 기존 산출물 개수 참고용이다.
- `session_20260616_212313_bpm120_beat2_small`은 중간에 노이즈가 낀 구간이 있으므로 학습 전 확인 또는 trim이 필요하다.
- Evaluation set은 `dataset/evaluation_transitions`에 별도로 저장한다.

Current intake audit:

```text
artifact: outputs/right_conducting/dataset_intake_audit.json
train_ready_count: 24
eval_scoreable_count: 1
eval_pending_relabel_count: 1
scoreable eval: session_20260616_222455_eval
pending relabel: session_20260616_215630_eval
```

Current staged zip smoke:

```text
artifact: outputs/right_conducting/recordings_staged_current.zip
manifest: outputs/right_conducting/recordings_staged_current_manifest.json
prepared dataset smoke: outputs/right_conducting/dataset_v0_60f_staged_current/manifest.json
goal runner smoke: outputs/right_conducting/right_conducting_goal_run_intake_stage_prepare_current.json
take_count: 24
60-frame window_count: 8006
```

새 데이터가 공급되면 학습 전에 먼저 실행한다.

```bash
python tools/audit_right_conducting_dataset_intake.py \
  --train-roots dataset/recordings,NEW_TRAIN_ROOT \
  --eval-roots dataset/evaluation_transitions,NEW_EVAL_ROOT \
  --output-json outputs/right_conducting/dataset_intake_audit_after_supply.json \
  --output-md outputs/right_conducting/dataset_intake_audit_after_supply.md
```

그 다음 canonical training zip을 만든다.

```bash
python tools/build_right_conducting_recordings_zip.py \
  --train-roots dataset/recordings,NEW_TRAIN_ROOT \
  --output-zip outputs/right_conducting/recordings_staged_after_supply.zip \
  --output-json outputs/right_conducting/recordings_staged_after_supply_manifest.json
```

## Active Training Recordings

| Session | BPM | Meter | Dynamics | Frames | Duration | 120-frame windows | Note |
|---------|-----|-------|----------|--------|----------|-------------------|------|
| `session_20260616_003523_bpm120_beat2` | 120 | 2박 | large | 2225 | 148.4s | 351 | ok |
| `session_20260616_005237_bpm120_beat3` | 120 | 3박 | large | 2174 | 145.1s | 343 | ok |
| `session_20260616_005614_bpm120_beat4` | 120 | 4박 | large | 2098 | 140.1s | 330 | ok |
| `session_20260616_174336_bpm060_beat2_large` | 60 | 2박 | large | 899 | 59.9s | 130 | ok |
| `session_20260616_174510_bpm060_beat3_large` | 60 | 3박 | large | 900 | 60.0s | 131 | ok |
| `session_20260616_174636_bpm060_beat4_large` | 60 | 4박 | large | 901 | 60.0s | 131 | ok |
| `session_20260616_180022_bpm060_beat2_small` | 60 | 2박 | small | 900 | 60.0s | 131 | ok |
| `session_20260616_180143_bpm060_beat3_small` | 60 | 3박 | small | 900 | 60.0s | 131 | ok |
| `session_20260616_210424_bpm060_beat4_small` | 60 | 4박 | small | 900 | 60.0s | 131 | ok |
| `session_20260616_210646_bpm080_beat2_large` | 80 | 2박 | large | 900 | 60.0s | 131 | ok |
| `session_20260616_210816_bpm080_beat3_large` | 80 | 3박 | large | 900 | 60.0s | 131 | ok |
| `session_20260616_210936_bpm080_beat4_large` | 80 | 4박 | large | 900 | 60.0s | 131 | ok |
| `session_20260616_211053_bpm080_beat2_small` | 80 | 2박 | small | 900 | 60.0s | 131 | ok |
| `session_20260616_211208_bpm080_beat3_small` | 80 | 3박 | small | 900 | 60.0s | 131 | ok |
| `session_20260616_211325_bpm080_beat4_small` | 80 | 4박 | small | 900 | 60.0s | 131 | ok |
| `session_20260616_211510_bpm100_beat2_large` | 100 | 2박 | large | 900 | 60.0s | 131 | ok |
| `session_20260616_211632_bpm100_beat3_large` | 100 | 3박 | large | 900 | 60.0s | 131 | ok |
| `session_20260616_211753_bpm100_beat4_large` | 100 | 4박 | large | 900 | 60.0s | 131 | ok |
| `session_20260616_211918_bpm100_beat2_small` | 100 | 2박 | small | 900 | 60.0s | 131 | ok |
| `session_20260616_212033_bpm100_beat3_small` | 100 | 3박 | small | 900 | 60.0s | 131 | ok |
| `session_20260616_212150_bpm100_beat4_small` | 100 | 4박 | small | 900 | 60.0s | 131 | ok |
| `session_20260616_212313_bpm120_beat2_small` | 120 | 2박 | small | 900 | 60.0s | 131 | middle-noise caution |
| `session_20260616_213424_bpm120_beat3_small` | 120 | 3박 | small | 897 | 60.0s | 130 | ok |
| `session_20260616_213543_bpm120_beat4_small` | 120 | 4박 | small | 900 | 60.0s | 131 | ok |

합계:

```text
active training recordings: 24
frames: 25394
120-frame windows: 3773
v0 training checklist: 24 / 24 complete
```

## Excluded From v0

- `140 BPM`
- `160 BPM`

## Excluded Recordings

- `session_20260615_222349_bpm120`
- `session_20260616_005205_bpm120_beat3`
