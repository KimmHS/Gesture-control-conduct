# Pose Quality Gate

## 목적

Live MediaPipe 입력에서는 오른어깨/팔꿈치/손목 confidence가 순간적으로 낮아질 수 있다. 기존 online buffer는 frame이 들어오면 항상 모델을 호출했기 때문에, tracking dropout 순간에 tempo/gain이 흔들릴 위험이 있었다.

이번 단계에서 online buffer에 right-arm validity gate를 추가했다. window 안 오른어깨/팔꿈치/손목의 valid ratio가 기준보다 낮으면 모델 호출을 건너뛰고 이전 MIDI 출력을 hold하며, output state에 invalid reason을 남긴다.

## 추가/수정된 코드

```text
lib/right_conducting/motionbert_pose_stream.py
tools/run_motionbert_pose_stream.py
tools/run_right_conducting_goal.py
lib/right_conducting/goal_status.py
lib/right_conducting/motionbert_export.py
tests/test_motionbert_pose_stream.py
tests/test_goal_command_cli.py
```

## Gate Rule

```text
right_arm_indices: [14, 15, 16]
right_arm_confidence_threshold: 0.0
valid_right_arm_ratio = min(valid_ratio(right_shoulder), valid_ratio(right_elbow), valid_ratio(right_wrist))
min_valid_right_arm_ratio: 0.8
if valid_right_arm_ratio < 0.8:
  do not call model
  hold previous live output
  state.valid = false
  state.invalid_reason = held_invalid_pose
```

처음부터 invalid이고 이전 출력이 없으면 fallback output을 내고 `state.invalid_reason = invalid_pose_no_previous`로 표시한다.

## 생성된 Artifact

```text
outputs/right_conducting/selected_motionbert_static80_transitions_live45f/degraded_static80_035040_pose.npy
outputs/right_conducting/selected_motionbert_static80_transitions_live45f/degraded_transition_022517_pose.npy
outputs/right_conducting/selected_motionbert_static80_transitions_live45f/degraded_online_pose_stream_static80_035040_live_outputs.jsonl
outputs/right_conducting/selected_motionbert_static80_transitions_live45f/degraded_online_pose_stream_static80_035040_summary.json
outputs/right_conducting/selected_motionbert_static80_transitions_live45f/degraded_online_pose_stream_transition_022517_live_outputs.jsonl
outputs/right_conducting/selected_motionbert_static80_transitions_live45f/degraded_online_pose_stream_transition_022517_summary.json
```

`motionbert_conducting_live_manifest.json`과 `motionbert_conducting_live_structure.md`에는 `pose_quality_gate_evidence`를 추가했다.

## Simulation

원본 pose에서 frame `90..150` 구간의 right shoulder/elbow/wrist confidence를 0으로 만들었다.

| case | rows | invalid | held invalid | tempo classes | raw switches | smoothed switches | gain switches |
|---|---:|---:|---:|---|---:|---:|---:|
| degraded static80 | 236 | 28 | 28 | `[1]` | 0 | 0 | 0 |
| degraded transition 022517 | 216 | 28 | 28 | `[1, 3]` | 6 | 2 | 0 |

해석:

```text
static80 dropout 구간에서도 tempo switch가 발생하지 않았다.
transition dropout 구간에서도 invalid windows는 이전 output을 hold했고, smoothed transition behavior는 기존 online stream과 동일하게 유지됐다.
```

## Goal Runner

```bash
python tools/run_right_conducting_goal.py \
  --steps pose-stream-selected \
  --motionbert-export-dir outputs/right_conducting/selected_motionbert_static80_transitions_live45f \
  --pose-stream-npy outputs/right_conducting/selected_motionbert_static80_transitions_live45f/degraded_transition_022517_pose.npy \
  --pose-stream-source-id degraded_transition_022517 \
  --pose-stream-online-buffer \
  --pose-stream-min-valid-right-arm-ratio 0.8 \
  --pose-stream-right-arm-confidence-threshold 0.0 \
  --pose-stream-output-jsonl outputs/right_conducting/selected_motionbert_static80_transitions_live45f/degraded_online_pose_stream_transition_022517_live_outputs.jsonl \
  --pose-stream-summary-json outputs/right_conducting/selected_motionbert_static80_transitions_live45f/degraded_online_pose_stream_transition_022517_summary.json
```

## Verification

```bash
python -m py_compile lib/right_conducting/motionbert_pose_stream.py tools/run_motionbert_pose_stream.py tools/run_right_conducting_goal.py
python -m unittest discover -s tests -p 'test_motionbert_pose_stream.py' -v
python -m unittest discover -s tests -p 'test_goal_command_cli.py' -v
```

결과:

```text
test_motionbert_pose_stream.py: 10 OK
test_goal_command_cli.py: 25 OK
```

## 남은 조건

Pose quality gate는 live robustness 장치다. strict heldout 일반화 점수는 여전히 `NO_GO`이며, 독립 fixed-camera heldout transition set으로 별도 검증해야 한다.
