# Live Output Contract

## 목적

선택된 MotionBERT 45f live bundle의 runtime 출력을 MIDI controller가 바로 소비할 수 있도록 schema artifact로 고정했다.

## 추가된 코드

```text
lib/right_conducting/live_output_contract.py
tools/export_motionbert_live_output_contract.py
tests/test_live_output_contract.py
```

## 생성된 artifact

```text
outputs/right_conducting/selected_motionbert_static80_transitions_live45f/live_output_contract.json
outputs/right_conducting/selected_motionbert_static80_transitions_live45f/live_output_contract.md
outputs/right_conducting/selected_motionbert_static80_transitions_live45f/live_output_sample.json
```

`motionbert_conducting_live_manifest.json`과 `motionbert_conducting_live_structure.md`에도 `live_output_contract_evidence`를 추가했다.

## Runtime Output

```text
schema_version: right_conducting_live_output_v1
tempo source: smoothed bpm
dynamics source: smoothed dynamics
gain class mapping: 0=small, 1=large
```

MIDI mapping:

| output | source | range |
|---|---|---:|
| tempo_bpm | smoothed tempo bpm | 60/80/100/120 |
| velocity_scale | smoothed dynamics | 0.35..1.00 |
| cc11_expression | smoothed dynamics | 32..127 |
| cc7_volume | unused | null |

Raw prediction은 monitoring/debugging용으로 유지하고, MIDI 제어에는 smoothed output을 사용한다.

## Verification

```bash
python -m py_compile lib/right_conducting/live_output_contract.py tools/export_motionbert_live_output_contract.py lib/right_conducting/motionbert_export.py
python -m unittest discover -s tests -p 'test_live_output_contract.py' -v
python -m unittest discover -s tests -p 'test_motionbert_export.py' -v
python tools/export_motionbert_live_output_contract.py \
  --manifest outputs/right_conducting/selected_motionbert_static80_transitions_live45f/motionbert_conducting_live_manifest.json \
  --update-manifest
```

결과:

```text
test_live_output_contract.py: 4 OK
test_motionbert_export.py: 3 OK
contract schema_version: right_conducting_live_output_v1
sample midi: tempo_bpm=120.0, velocity_scale=0.818, cc11_expression=100
```

## 남은 조건

이 작업은 live 출력 계약을 고정한 것이고, strict heldout 일반화 증거를 새로 만든 것은 아니다. 현재 goal 상태는 그대로 `live pilot GO`, `strict heldout NO_GO`다.
