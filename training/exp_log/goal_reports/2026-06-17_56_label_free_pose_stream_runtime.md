# Label-Free Pose Stream Runtime

## 목적

실제 stream 환경에서는 `labels_frame.jsonl`이 없다. 기존 replay 경로는 score 계산을 위해 label을 읽었으므로, 최종 runtime 검증에는 label 없는 pose buffer 경로가 따로 필요했다.

이번 단계에서 `pose_right_h36m_masked.npy`만 입력으로 받아 sliding window inference를 수행하고, 각 update를 `right_conducting_live_output_v1` JSONL로 내보내는 경로를 추가했다.

## 추가/수정된 코드

```text
lib/right_conducting/motionbert_pose_stream.py
tools/run_motionbert_pose_stream.py
tools/run_right_conducting_goal.py
lib/right_conducting/goal_status.py
tests/test_motionbert_pose_stream.py
tests/test_goal_command_cli.py
tests/test_goal_status.py
```

## Runtime Flow

```text
pose_right_h36m_masked.npy [T,17,3]
  -> sliding window, window=45f, stride=3f
  -> MotionBERTLivePredictor.predict_window()
  -> LiveSmoother.update()
  -> right_conducting_live_output_v1 JSONL
  -> MIDI tempo_bpm / velocity_scale / CC11 expression
```

이 경로는 label을 읽지 않는다.

## 생성된 Artifact

```text
outputs/right_conducting/selected_motionbert_static80_transitions_live45f/pose_stream_static80_035040_live_outputs.jsonl
outputs/right_conducting/selected_motionbert_static80_transitions_live45f/pose_stream_static80_035040_summary.json
outputs/right_conducting/selected_motionbert_static80_transitions_live45f/pose_stream_transition_022517_live_outputs.jsonl
outputs/right_conducting/selected_motionbert_static80_transitions_live45f/pose_stream_transition_022517_summary.json
```

`motionbert_conducting_live_manifest.json`과 `motionbert_conducting_live_structure.md`에는 `pose_stream_evidence`를 추가했다.

## 결과

| case | rows | time span | tempo classes | raw tempo switches | smoothed tempo switches | gain switches |
|---|---:|---:|---|---:|---:|---:|
| static80 high-arm small | 236 | 3.0s..50.0s | `[1]` | 0 | 0 | 0 |
| transition 022517 beat3 small | 216 | 3.0s..46.0s | `[1, 3]` | 6 | 2 | 0 |

해석:

```text
static80 pose stream은 label 없이도 80 BPM만 유지했다.
transition pose stream은 120/80 class가 모두 나오며, smoother가 raw switch 6개를 smoothed switch 2개로 줄였다.
이 결과는 점수표가 아니라 runtime wiring evidence다.
```

## Goal Runner

```bash
python tools/run_right_conducting_goal.py \
  --steps pose-stream-selected \
  --motionbert-export-dir outputs/right_conducting/selected_motionbert_static80_transitions_live45f \
  --pose-stream-npy dataset/transitions/session_20260617_022517_bpm120to120_beat3_small/pose_right_h36m_masked.npy \
  --pose-stream-source-id session_20260617_022517_bpm120to120_beat3_small \
  --pose-stream-output-jsonl outputs/right_conducting/selected_motionbert_static80_transitions_live45f/pose_stream_transition_022517_live_outputs.jsonl \
  --pose-stream-summary-json outputs/right_conducting/selected_motionbert_static80_transitions_live45f/pose_stream_transition_022517_summary.json
```

## Verification

```bash
python -m py_compile lib/right_conducting/motionbert_pose_stream.py tools/run_motionbert_pose_stream.py
python -m unittest discover -s tests -p 'test_motionbert_pose_stream.py' -v
python -m unittest discover -s tests -p 'test_goal_command_cli.py' -v
python -m unittest discover -s tests -p 'test_goal_status.py' -v
```

결과:

```text
test_motionbert_pose_stream.py: 5 OK
test_goal_command_cli.py: 25 OK
test_goal_status.py: 2 OK
```

## 남은 조건

이 단계는 label-free runtime evidence를 추가한 것이다. strict heldout 일반화 점수는 아직 `NO_GO`이며, 독립 fixed-camera heldout transition set이 필요하다.
