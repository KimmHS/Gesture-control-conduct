# Online Pose Frame Buffer

## 목적

`pose_right_h36m_masked.npy` 전체 배열을 한 번에 순회하는 label-free runner는 실제 stream과 아직 다르다. 실제 runtime에서는 pose frame이 하나씩 들어오고, rolling buffer가 window를 만들며, stride마다 모델을 호출한다.

이번 단계에서 frame-by-frame online buffer를 추가하고, 같은 pose sequence에서 기존 window-scan 결과와 online-buffer 결과가 일치하는지 확인했다.

## 추가/수정된 코드

```text
lib/right_conducting/motionbert_pose_stream.py
tools/run_motionbert_pose_stream.py
tools/run_right_conducting_goal.py
tests/test_motionbert_pose_stream.py
tests/test_goal_command_cli.py
lib/right_conducting/goal_status.py
lib/right_conducting/motionbert_export.py
```

## Runtime Flow

```text
pose frame [17,3]
  -> OnlinePoseFrameStreamer.push_frame()
  -> rolling buffer [45,17,3]
  -> every 3 frames, MotionBERTLivePredictor.predict_window()
  -> LiveSmoother.update()
  -> right_conducting_live_output_v1 JSONL
```

첫 출력은 45 frames가 쌓인 뒤 나온다. 현재 설정에서는 `45f / 15fps = 3.0s` cold start이고, 이후 `stride=3f`, 즉 약 0.2초마다 update된다.

## 생성된 Artifact

```text
outputs/right_conducting/selected_motionbert_static80_transitions_live45f/online_pose_stream_static80_035040_live_outputs.jsonl
outputs/right_conducting/selected_motionbert_static80_transitions_live45f/online_pose_stream_static80_035040_summary.json
outputs/right_conducting/selected_motionbert_static80_transitions_live45f/online_pose_stream_transition_022517_live_outputs.jsonl
outputs/right_conducting/selected_motionbert_static80_transitions_live45f/online_pose_stream_transition_022517_summary.json
outputs/right_conducting/selected_motionbert_static80_transitions_live45f/online_pose_stream_comparison.json
outputs/right_conducting/selected_motionbert_static80_transitions_live45f/online_pose_stream_comparison.md
```

`motionbert_conducting_live_manifest.json`과 `motionbert_conducting_live_structure.md`에는 `online_pose_stream_evidence`를 추가했다.

## 결과

| case | mode | rows | tempo classes | raw switches | smoothed switches |
|---|---|---:|---|---:|---:|
| static80 high-arm small | online_buffer | 236 | `[1]` | 0 | 0 |
| transition 022517 beat3 small | online_buffer | 216 | `[1, 3]` | 6 | 2 |

Comparison:

```text
status: PASS
ignore_fields: source.source_id
static80 window-scan rows == online rows: 236 == 236
transition window-scan rows == online rows: 216 == 216
first_mismatch_indices: []
```

## Goal Runner

```bash
python tools/run_right_conducting_goal.py \
  --steps pose-stream-selected \
  --motionbert-export-dir outputs/right_conducting/selected_motionbert_static80_transitions_live45f \
  --pose-stream-npy dataset/transitions/session_20260617_022517_bpm120to120_beat3_small/pose_right_h36m_masked.npy \
  --pose-stream-source-id session_20260617_022517_bpm120to120_beat3_small_online \
  --pose-stream-online-buffer \
  --pose-stream-output-jsonl outputs/right_conducting/selected_motionbert_static80_transitions_live45f/online_pose_stream_transition_022517_live_outputs.jsonl \
  --pose-stream-summary-json outputs/right_conducting/selected_motionbert_static80_transitions_live45f/online_pose_stream_transition_022517_summary.json
```

## Verification

```bash
python -m py_compile lib/right_conducting/motionbert_pose_stream.py tools/run_motionbert_pose_stream.py tools/run_right_conducting_goal.py
python -m unittest discover -s tests -p 'test_motionbert_pose_stream.py' -v
python -m unittest discover -s tests -p 'test_goal_command_cli.py' -v
python -m unittest discover -s tests -p 'test_goal_status.py' -v
```

결과:

```text
test_motionbert_pose_stream.py: 7 OK
test_goal_command_cli.py: 25 OK
test_goal_status.py: 2 OK
online_pose_stream_comparison: PASS
```

## 남은 조건

Online runtime wiring은 더 강해졌지만, strict heldout 일반화는 여전히 `NO_GO`다. 독립 fixed-camera heldout transition set으로 `heldout-independence,replay-selected,live-output,live-replay-gate`를 다시 돌려야 최종 score claim이 가능하다.
