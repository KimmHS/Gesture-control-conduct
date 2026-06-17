# Live Output Replay Adapter

## 목적

선택된 MotionBERT live bundle의 replay 결과를 실제 stream/MIDI runtime이 소비할 `right_conducting_live_output_v1` JSONL로 변환하는 경로를 추가했다.

이 단계는 모델 score를 새로 올리는 작업이 아니라, 이미 선택된 모델의 raw/smoothed prediction이 downstream MIDI control로 같은 schema를 통해 흘러가도록 고정하는 작업이다.

## 추가/수정된 코드

```text
lib/right_conducting/live_output_contract.py
lib/right_conducting/motionbert_replay.py
tools/convert_motionbert_replay_rows_to_live_outputs.py
tools/smoke_motionbert_live_bundle.py
tests/test_live_output_contract.py
tests/test_motionbert_live.py
tests/test_motionbert_replay.py
```

## Runtime 흐름

```text
MotionBERT raw prediction
  -> LiveSmoother smoothed prediction
  -> right_conducting_live_output_v1
  -> MIDI tempo_bpm / velocity_scale / CC11 expression
```

Replay 검증 흐름:

```text
replay_*_rows.jsonl
  -> convert_motionbert_replay_rows_to_live_outputs.py
  -> live_outputs_*_stable.jsonl
```

## 생성된 artifact

```text
outputs/right_conducting/selected_motionbert_static80_transitions_live45f/live_outputs_static80_stable.jsonl
outputs/right_conducting/selected_motionbert_static80_transitions_live45f/live_outputs_static80_stable_summary.json
outputs/right_conducting/selected_motionbert_static80_transitions_live45f/live_outputs_transitions_stable.jsonl
outputs/right_conducting/selected_motionbert_static80_transitions_live45f/live_outputs_transitions_stable_summary.json
```

`motionbert_conducting_live_manifest.json`과 `motionbert_conducting_live_structure.md`에는 `live_output_replay_evidence`를 추가했다.

## Summary

| source | rows | tempo classes | gain classes | first MIDI | last MIDI |
|---|---:|---|---|---|---|
| static80 stable | 942 | `[1]` | `[0, 1]` | `80.0 bpm / vel 0.854 / CC11 106` | `80.0 bpm / vel 0.548 / CC11 61` |
| transitions stable | 1305 | `[1, 2, 3]` | `[0, 1]` | `120.0 bpm / vel 0.822 / CC11 101` | `100.0 bpm / vel 0.573 / CC11 65` |

## Verification

```bash
python -m py_compile \
  lib/right_conducting/motionbert_replay.py \
  tools/smoke_motionbert_live_bundle.py \
  tools/convert_motionbert_replay_rows_to_live_outputs.py \
  lib/right_conducting/live_output_contract.py

python -m unittest discover -s tests -p 'test_motionbert_live.py' -v
python -m unittest discover -s tests -p 'test_motionbert_replay.py' -v
python -m unittest discover -s tests -p 'test_live_output_contract.py' -v
python -m unittest discover -s tests -p 'test_goal_command_cli.py' -v
```

결과:

```text
test_motionbert_live.py: 6 OK
test_motionbert_replay.py: 3 OK
test_live_output_contract.py: 6 OK
test_goal_command_cli.py: 24 OK
```

## Goal Runner

Strict heldout replay를 받을 때는 다음 순서로 live output JSONL까지 같이 만들 수 있다.

```bash
python tools/run_right_conducting_goal.py \
  --steps heldout-independence,replay-selected,live-output,live-replay-gate \
  --heldout-train-manifests outputs/right_conducting/recordings_staged_static80_transitions_manifest.json \
  --heldout-eval-roots dataset/evaluation_transitions_v1 \
  --motionbert-export-dir outputs/right_conducting/selected_motionbert_static80_transitions_live45f \
  --motionbert-replay-eval-root dataset/evaluation_transitions_v1 \
  --motionbert-replay-stable-only \
  --motionbert-replay-output-rows outputs/right_conducting/strict_heldout_transition_replay_v1_rows.jsonl \
  --live-output-jsonl outputs/right_conducting/strict_heldout_transition_live_outputs_v1.jsonl \
  --live-output-summary-json outputs/right_conducting/strict_heldout_transition_live_outputs_v1_summary.json \
  --live-replay-gate-require-independence
```

## 남은 조건

현재 `dataset/static_variants_80`과 `dataset/transitions` score는 deployment-fit evidence다. strict heldout 일반화는 아직 `NO_GO`이고, 독립 fixed-camera heldout transition set이 필요하다.
