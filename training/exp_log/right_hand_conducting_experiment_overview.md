# Right-Hand Conducting Experiment Overview

이 문서는 빠른 입구용 요약이다. 최종 상세 plan은 아래 문서가 canonical source다.

```text
docs/exp/final_plan_motionbert_lite_conducting_control.md
```

## Current Final Direction

```text
right hand / right arm / right shoulder motion
  -> MediaPipe Pose 33
  -> H36M 17 conversion
  -> right-arm masked H36M17 sequence
  -> MotionBERT-Lite frozen encoder
  -> train conducting head only
  -> tempo class + BPM distribution + dynamics regression
  -> MIDI tempo / velocity / CC11 control
```

## What Changed

이전 draft의 `TCN comparison`과 `dynamics classification` 방향은 제외한다. `4-class tempo`는 현재 v0 데이터 범위이고, `6-class tempo`는 추가 데이터 수집 후 final target이다.

최종 방향:

- Backbone: MotionBERT-Lite frozen encoder
- Trainable part: lightweight conducting head only
- Current v0 tempo: 4-class `60 / 80 / 100 / 120`
- Final tempo target: 6-class `60 / 80 / 100 / 120 / 140 / 160`
- Current v0 FPS/window: about 15fps, 60 frames ~= 4s
- Tempo smoothing target: `bpm_distribution`
- Dynamics: continuous regression `0.0 ~ 1.0`
- Augmentation: label-preserving plus label-changing `temporal_stretch` / `amplitude_scaling` with target updates
- Baselines: existing rule-based control and hand-crafted feature ML baseline must be reported
- Control target: MIDI tempo, velocity scale, CC11 Expression
- Left hand: model input에서 제외, rule-based UI control only

## Quick Links

| 찾고 싶은 내용 | 문서 |
|---|---|
| 최종 계획 전체 | [final_plan_motionbert_lite_conducting_control.md](final_plan_motionbert_lite_conducting_control.md) |
| 구현 폴더 구조 | [final plan: Folder Structure](final_plan_motionbert_lite_conducting_control.md#15-folder-structure) |
| 데이터셋 구조 | [final plan: Dataset](final_plan_motionbert_lite_conducting_control.md#3-dataset) |
| annotation | [final plan: Annotation](final_plan_motionbert_lite_conducting_control.md#7-annotation) |
| augmentation | [final plan: Augmentation](final_plan_motionbert_lite_conducting_control.md#9-augmentation) |
| streaming runtime | [final plan: Streaming Runtime](final_plan_motionbert_lite_conducting_control.md#12-streaming-runtime) |
| MIDI mapping | [final plan: MIDI Control Mapping](final_plan_motionbert_lite_conducting_control.md#13-midi-control-mapping) |
| current risks | [final plan: Current Risks and Required Reporting](final_plan_motionbert_lite_conducting_control.md#145-current-risks-and-required-reporting) |
| current/final contradictions | [contradictions.md](contradictions.md) |
| feedback mapping | [mid_presentation_feedback.md](mid_presentation_feedback.md) |
| goal command | [final plan: Goal Command](final_plan_motionbert_lite_conducting_control.md#19-goal-command) |

## Current Important Paths

```text
dataset/recordings.zip
checkpoint/MB_lite.yaml
checkpoint/mb_lite_v0.pt
checkpoint/latest_epoch (1).bin
dataset/evaluation_transitions/session_20260616_222455_eval
dataset/evaluation_transitions/session_20260616_215630_eval  # relabel 전까지 score 제외
```
