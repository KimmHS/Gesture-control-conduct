# Final Plan: Right-Hand MotionBERT-Lite Conducting Control

## Quick Navigation

| 찾고 싶은 내용 | 섹션 |
|---|---|
| 최종 결정 | [0. Final Decision](#0-final-decision) |
| 현재 v0 범위 | [0.5 Current v0 Scope](#05-current-v0-scope) |
| 프로젝트 목표와 출력 | [1. Goal](#1-goal) |
| 모델 입력/구조/loss | [2. Model](#2-model) |
| 데이터셋 구조 | [3. Dataset](#3-dataset) |
| 1명 pilot 수집량 | [4. Pilot Dataset](#4-pilot-dataset) |
| 최종 데이터 규모 | [5. Final Dataset Scale](#5-final-dataset-scale) |
| recording protocol | [6. Recording Protocol](#6-recording-protocol) |
| annotation 방법 | [7. Annotation](#7-annotation) |
| normalization | [8. Normalization](#8-normalization) |
| augmentation | [9. Augmentation](#9-augmentation) |
| split 정책 | [10. Split Policy](#10-split-policy) |
| 학습 단계 | [11. Training Plan](#11-training-plan) |
| streaming runtime | [12. Streaming Runtime](#12-streaming-runtime) |
| MIDI 연결 | [13. MIDI Control Mapping](#13-midi-control-mapping) |
| 평가 지표 | [14. Metrics](#14-metrics) |
| 현재 한계와 보완책 | [14.5 Current Risks and Required Reporting](#145-current-risks-and-required-reporting) |
| 구현 폴더 구조 | [15. Folder Structure](#15-folder-structure) |
| 실행 순서 | [16. Execution Phases](#16-execution-phases) |
| 발표 요약 문장 | [17. Presentation Summary](#17-presentation-summary) |
| 최종 산출물 | [18. Deliverables](#18-deliverables) |
| goal command | [19. Goal Command](#19-goal-command) |

## 0. Final Decision

프로젝트 방향은 아래 구조로 고정한다.

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

왼손은 딥러닝 모델 입력에 넣지 않는다.

```text
left hand:
  instrument selection / mute / cue
  -> rule-based UI logic

right hand:
  global conducting
  -> deep learning model input
```

이 구조는 “오른손 = global conducting, 왼손 = instrument-level control” 방향과 일치한다. 기존 wrist velocity / motion radius 기반 rule baseline은 유지하고, 딥러닝 모델의 비교 기준과 fallback으로 사용한다.

## 0.5 Current v0 Scope

현재 workspace의 v0 데이터는 final target과 범위가 다르다. 실험 보고와 goal 구현은 아래 범위를 기본값으로 둔다.

```text
current v0 fps: about 15fps
current v0 tempo bins: 60 / 80 / 100 / 120 BPM
current v0 default window: 60 frames ~= 4s
current v0 default stride: 3 frames ~= 0.2s
120-frame windows on current data: ~= 8s long-window ablation, not 4s
```

Final target은 충분한 데이터가 추가된 뒤 아래 범위로 확장한다.

```text
final target fps: 30fps or explicit 30fps resampling
final tempo bins: 60 / 80 / 100 / 120 / 140 / 160 BPM
final default window at 30fps: 120 frames = 4s
final default stride at 30fps: 6 frames = 0.2s
```

## 1. Goal

최종 목표는 오른손 지휘 motion으로 MIDI playback의 tempo와 dynamics를 실시간 제어하는 시스템을 구현하는 것이다.

### Outputs

| Output | Meaning | MIDI 연결 |
|---|---|---|
| `tempo_class` | v0: `60 / 80 / 100 / 120 BPM`; final: add `140 / 160 BPM` | playback tempo |
| `bpm_distribution` | 주변 BPM까지 포함한 soft distribution | tempo smoothing |
| `dynamics` | `0.0 ~ 1.0` continuous intensity | velocity scale / CC11 Expression |
| `state` optional | `conducting / invalid` | fallback control |

WAV speed/volume 제어보다 MIDI tempo, velocity, CC11 Expression 제어가 지휘 demo 목적에 더 맞다.

## 2. Model

### 2.1 Input

Pipeline:

```text
raw webcam frame
  -> MediaPipe Pose 33
  -> H36M 17 conversion
  -> right-arm masked H36M17
```

Final tensor:

```python
x_body.shape = [B, T, 17, 3]
```

Recommended channels:

```text
x_norm
y_norm
confidence
```

MotionBERT는 H36M 17-joint format을 사용하므로 MediaPipe 33 landmark를 H36M 17로 변환한 뒤 입력한다. 입력 길이는 `243` frames 이하 variable length를 기준으로 운용한다.

### 2.2 Right-Arm Masking

MotionBERT-Lite는 17-joint shape을 기대하므로 shape은 유지한다. 실제 정보는 오른쪽 팔 중심으로 제한한다.

Keep:

```text
neck / shoulder_center
right shoulder
right elbow
right wrist
optional left shoulder for normalization reference
```

Mask:

```text
all other joints: confidence = 0
```

Core right-arm indices:

```python
right_indices = [14, 15, 16]  # right shoulder, right elbow, right wrist
```

왼쪽 어깨는 왼손 제어 정보가 아니라 shoulder-width normalization 기준이다.

### 2.3 Backbone

Backbone은 pretrained MotionBERT-Lite encoder를 사용하고 freeze한다.

```text
MotionBERT-Lite pretrained encoder
  -> frozen
```

Workspace checkpoint:

```text
checkpoint/MB_lite.yaml
checkpoint/mb_lite_v0.pt          # symlink to latest_epoch (1).bin
checkpoint/latest_epoch (1).bin   # original downloaded filename
```

Use `checkpoint/mb_lite_v0.pt` in scripts and configs. The original filename contains spaces and parentheses, which is easy to break in shell commands.

### 2.4 Conducting Head

MotionBERT-Lite representation에서 오른팔 token만 pooling한다.

```python
E = motionbert_lite.get_representation(x_body)  # [B, T, 17, D]
E_right = E[:, :, right_indices, :]
z = E_right.mean(dim=(1, 2))
```

Do not flatten all `17 x D` tokens into the head by default. Most joints are masked and can add noise/capacity waste. The v0 head pools only right-arm tokens. An ablation may compare:

```text
right-arm pooling: [14, 15, 16]
valid-context pooling: [8, 9, 11, 14, 15, 16]
```

Use mask-aware pooling if context joints are included:

```python
valid = x_body[..., 2] > 0
z = (E * valid[..., None]).sum(dim=(1, 2)) / valid.sum(dim=(1, 2)).clamp_min(1.0)[:, None]
```

Head:

```text
z
  -> MLP
  -> tempo_class_head
  -> bpm_distribution_head
  -> dynamics_head
```

Outputs:

```text
tempo_class_logits: [B, C]
bpm_distribution_logits: [B, C]
dynamics: [B, 1]
```

Loss:

```python
loss = (
    ce_tempo_class
    + kl_bpm_distribution
    + smooth_l1_dynamics
)
```

The BPM distribution is not optional in v0. Small data benefits from soft targets because `100 BPM` can still teach neighboring `80/120 BPM` bins through the KL term.

Tempo classes:

```python
BPM_BINS_V0 = [60, 80, 100, 120]
BPM_BINS_FINAL = [60, 80, 100, 120, 140, 160]
```

Frame-length handling:

```text
MotionBERT-Lite maxlen: 243 frames
v0 default on current 15fps data: 60 frames
v0 long-window ablation: 120 frames
final 30fps target: 120 frames
```

The existing `DSTformer` slices temporal positional embedding as `temp_embed[:, :F]`, so no interpolation is needed for `F <= 243`. Add smoke tests for `T=60`, `T=120`, and `T=180` to catch shape or checkpoint-loading errors before training.

## 3. Dataset

Dataset name:

```text
RightHand-Conducting-Control-v0
```

Recommended target structure for new/final dataset:

```text
dataset/
  right_conducting_v0/
    P01/
      S001_front/
        calibration/
          meta.json
          raw_video.mp4
          calibration.json
        take_001_60bpm_neutral/
          meta_take.json
          raw_video.mp4
          pose_33_mediapipe.npy
          pose_17_h36m.npy
          pose_right_h36m_masked.npy
          right_arm_3joints.npy
          right_rule_features.npy
          labels_window.jsonl
          quality_report.json
```

Current training source in this workspace:

```text
dataset/recordings.zip
```

Current workspace limitation:

```text
The current archive appears to be a small, likely single-subject dataset.
Take-level split helps prevent window leakage, but it does not prove cross-subject generalization.
All reports and model cards must explicitly label current results as single-subject / subject-specific unless multi-subject data is collected.
```

### File Roles

| File | Content | Purpose |
|---|---|---|
| `raw_video.mp4` | 원본 영상 | reprocessing, debugging |
| `pose_33_mediapipe.npy` | `[T, 33, 3]` | MediaPipe 원본 pose |
| `pose_17_h36m.npy` | `[T, 17, 3]` | MotionBERT 변환 전 full skeleton |
| `pose_right_h36m_masked.npy` | `[T, 17, 3]` | 실제 모델 입력 |
| `right_arm_3joints.npy` | `[T, 3, 3]` | 오른어깨/팔꿈치/손목 확인 |
| `right_rule_features.npy` | velocity, radius 등 | rule baseline |
| `labels_window.jsonl` | window labels | training target |
| `quality_report.json` | tracking quality | reject / warn / pass |

PyTorch `Dataset.__len__`, `Dataset.__getitem__`, 필요 시 `collate_fn`으로 window sample을 반환한다.

## 4. Pilot Dataset

1명 dataset은 최종 일반화 성능 주장이 아니라 아래 검증용이다.

1. recording UI 검증
2. MediaPipe tracking 품질 확인
3. H36M17 변환 확인
4. MotionBERT-Lite 입력 shape 확인
5. conducting head 학습 가능성 확인
6. subject-specific demo 확보

Recommended amount:

```text
minimum: 20 min
recommended: 40 min
stable: 60 min
```

### 1-Person Final-Target Collection Table

현재 v0 이미 수집된 데이터는 `60/80/100/120 BPM`만 포함한다. 아래 표는 추가 촬영 시 final 6-class target으로 확장하기 위한 권장표다.

| Block | Condition | Take | Duration |
|---|---|---|---|
| Calibration | still, small motion, large motion | `1 x 60s` | 1 min |
| Tempo | `60/80/100/120/140/160 BPM` | each `2 x 60s` | 12 min |
| Dynamics | `small/neutral/large/crescendo/diminuendo` | each `2 x 60s` | 10 min |
| Mixed | `80/120/160 x small/neutral/large` | each `2 x 30s` | 9 min |
| Free conducting | natural conducting | `1~2 takes` | 3~5 min |
| Holdout test | excluded from train | `7 x 30s` | 3.5 min |

Total:

```text
about 38~41 min
```

## 5. Final Dataset Scale

Recommended final scale:

```text
5 people x 45~60 min
= about 3.75~5 hours raw recording
```

Minimum presentation scale:

```text
3 people x 30~40 min
= about 1.5~2 hours raw recording
```

Class-level target:

```text
tempo class:
  minimum 10 min raw video per class
  recommended 15+ min per class

dynamics condition:
  minimum 5 min
  recommended 10 min
```

Heldout evaluation target before final reporting:

```text
stable hold:
  at least 3 takes
  examples: 100/4/large, 100/4/small, 120/4/large

transition:
  at least 2~3 takes
  examples: 60 -> 100, 100 -> 60, 100 -> 120, large -> small, small -> large
```

The current scoreable heldout set is only:

```text
dataset/evaluation_transitions/session_20260616_222455_eval
```

Evaluation input policy for this session:

```text
use:
  labels_window.jsonl
  pose_right_h36m_masked.npy
  right_rule_features.npy
ignore for scoring:
  recommended_augmented_v0/
  labels_tempo_augmented_15f.jsonl
  tempo_augmented_15f.npy
```

`manual_timeline.json` records an ambiguous event at `33.0s`. Score reports must state how mixed/ambiguous windows are handled before using switch-latency or false-switch metrics.

Do not treat one transition session as a statistically stable estimate. Report it as an early heldout check until more heldout recordings are labeled.

## 6. Recording Protocol

Camera:

```text
resolution: 640x480 or higher
current v0 fps: about 15
final target fps: 30, or explicit 30fps resampling before windowing
distance: 1.5~2m
view: front
framing: head, neck, both shoulders, right shoulder, right elbow, right wrist, right hand, waist area
```

Even though only right-arm features are used by the model, the full upper body should be visible. Both shoulders are needed for stable shoulder-width normalization.

Avoid:

```text
right hand leaves frame
right elbow occluded by body
arm color too similar to background
backlight
camera shake
large posture/distance changes between takes
```

## 7. Annotation

Do not manually label every frame. Use prompt-driven metadata, automatic motion features, and partial manual review.

### 7.1 Take-Level Metadata

Recording UI saves metadata:

```json
{
  "person_id": "P01",
  "session_id": "S001",
  "take_id": "take_007_120bpm_neutral",
  "fps_estimate": 14.985,
  "camera_view": "front",
  "meter": 4,
  "bpm_prompt": 120,
  "tempo_class": 3,
  "dynamics_prompt": "neutral",
  "take_type": "tempo"
}
```

### 7.2 Window-Level Labels

Training is window-based, not frame-based.

Recommended default:

```text
current v0: 60 frames ~= 4s at 15fps, stride 3 frames ~= 0.2s
current v0 long-window ablation: 120 frames ~= 8s at 15fps
final 30fps target: 120 frames = 4s, stride 6 frames = 0.2s
```

Example `labels_window.jsonl` row:

```json
{
  "window_id": "take_007_w0001",
  "start": 45,
  "end": 105,
  "tempo_class": 3,
  "bpm_target": 120,
  "bpm_distribution": [0.00, 0.02, 0.29, 0.69],
  "dynamics_target": 0.50,
  "dynamics_prompt": "neutral",
  "valid_right_arm_ratio": 0.98,
  "quality": "pass"
}
```

### 7.3 Tempo Label

```text
0: 60 BPM
1: 80 BPM
2: 100 BPM
3: 120 BPM
```

`140 / 160 BPM`은 final 6-class target에 포함하지만 current v0 score에는 넣지 않는다.

Soft BPM distribution:

```python
bins = [60, 80, 100, 120]  # current v0
target = bpm_prompt
sigma = 15
p_i = exp(-((bins[i] - target) ** 2) / (2 * sigma ** 2))
p_i = p_i / sum(p_i)
```

### 7.4 Dynamics Label

Initial prompt targets:

```text
small      -> 0.25
neutral    -> 0.50
large      -> 0.80
crescendo  -> 0.25 -> 0.85
diminuendo -> 0.85 -> 0.25
```

Measured target:

```python
dynamics_measured = normalize(
    right_wrist_motion_radius,
    calibration_small_radius,
    calibration_large_radius,
)
```

v0 target choices:

```text
stability first:
  dynamics_target = prompt value

control feel first:
  dynamics_target = measured value

balanced:
  dynamics_target = 0.5 * prompt_value + 0.5 * measured_value
```

Recommended v0:

```text
dynamics_target = 0.5 * prompt_value + 0.5 * measured_value
```

## 8. Normalization

Primary normalization:

```python
origin = midpoint(left_shoulder, right_shoulder)
scale = distance(left_shoulder, right_shoulder)
x_norm = (x - origin_x) / scale
y_norm = (y - origin_y) / scale
```

Fallback normalization:

```python
origin = right_shoulder
scale = distance(right_shoulder, right_elbow) + distance(right_elbow, right_wrist)
```

For pilot, save both:

```text
pose_right_h36m_masked_shoulder_center.npy
pose_right_h36m_masked_right_shoulder.npy
```

Required ablation:

```text
camera coordinates
shoulder_center normalization
right_shoulder/right_arm_length normalization
```

At least one fold or pilot run must compare these modes in the score table. If evaluation recordings use different distance/framing, normalized modes should be preferred unless they clearly underperform.

## 9. Augmentation

### 9.1 Label-Preserving Augmentation

Keep labels unchanged:

```text
random window offset
coordinate jitter
smooth motion noise
confidence dropout
small translation
small rotation
small scale jitter
```

Recommended config:

```yaml
augmentation_v0:
  window_offset:
    max_offset_frames: 5
  coordinate_jitter:
    sigma: 0.01
  smooth_motion_noise:
    sigma: 0.005
    alpha: 0.8
  confidence_dropout:
    prob_wrist: 0.03
    prob_elbow: 0.02
    prob_shoulder: 0.01
    max_len_frames: 5
  translation:
    dx_range: [-0.03, 0.03]
    dy_range: [-0.03, 0.03]
  scale:
    range: [0.95, 1.05]
  rotation:
    degree_range: [-5, 5]
```

### 9.2 Label-Changing Augmentation

Use in v0 because the current dataset is small. Labels must be updated together.

| Augmentation | Updated Label |
|---|---|
| `temporal_stretch` | `bpm_target`, `bpm_distribution` |
| `amplitude_scaling` | `dynamics_target` |

```python
bpm_aug = bpm_original * stretch_factor
dynamics_aug = clip(dynamics_original * amplitude_scale, 0.0, 1.0)
```

Recommended v0 ranges:

```yaml
label_changing_augmentation_v0:
  temporal_stretch:
    factors: [0.90, 0.95, 1.05, 1.10]
    update_bpm_distribution: true
    keep_if_bpm_in_range: [60, 120]
    bins: [60, 80, 100, 120]
  amplitude_scaling:
    factors: [0.80, 0.90, 1.10, 1.20]
    update_dynamics_target: true
```

For temporal stretch, recompute soft BPM distribution after stretching:

```python
bpm_aug = bpm_original * stretch_factor
p_i = exp(-((bins[i] - bpm_aug) ** 2) / (2 * sigma ** 2))
p_i = p_i / sum(p_i)
tempo_class = argmin(abs(bins - bpm_aug))
```

For amplitude scaling:

```python
dynamics_aug = clip(dynamics_target * amplitude_scale, 0.0, 1.0)
```

Keep label-changing augmentation in train split only. Validation/test/heldout must stay real recordings.

### 9.3 Forbidden

```text
horizontal flip
```

Reason: the model semantics are right-hand global conducting.

### 9.4 Application Order

```text
raw take-level split
  -> train split only: augmentation
  -> validation/test: original real recordings only
```

Never let windows from the same original take appear in both train and validation.

## 10. Split Policy

### 10.1 1-Person Pilot

```text
Train:
  tempo block take 1
  dynamics block take 1
  part of mixed block

Validation:
  part of tempo block take 2
  part of dynamics block take 2

Test:
  holdout test block
  preferably another-day session
```

Forbidden:

```text
windows from the same 60s take split across train and validation
```

### 10.2 5-Person Final

Option A:

```text
Train: P01, P02, P03
Validation: P04
Test: P05
```

Option B if data is limited:

```text
leave-one-subject-out evaluation
```

## 11. Training Plan

### Stage 0: Keep Rule Baseline

Existing rule baseline remains:

```text
right wrist velocity -> tempo estimate
right motion radius -> dynamics estimate
```

Use as:

```text
baseline
fallback
sanity check
```

The score table must include a rule-based baseline row:

```text
right_rule_features.npy
  -> wrist speed / beat periodicity estimate for tempo
  -> shoulder-wrist radius for dynamics
  -> same validation / heldout metrics as the learned model
```

### Stage 0.5: Hand-Crafted Feature ML Baseline

Add a small-data baseline using `right_rule_features.npy`.

Inputs:

```text
wrist_vx
wrist_vy
wrist_speed
shoulder_wrist_radius
elbow_angle_rad
right_arm_valid
```

Targets:

```text
tempo_class
bpm_distribution or bpm_target
dynamics_target
```

Recommended models:

```text
logistic / ridge head implemented in PyTorch
or RandomForest/SVM only if scikit-learn is already available
```

Purpose:

```text
If hand-crafted ML matches MotionBERT head, the dataset is too small or too rule-like to justify a larger model.
```

### Stage 1: MotionBERT-Lite Embedding Cache

```text
pose_right_h36m_masked.npy
  -> MotionBERT-Lite frozen forward
  -> body_embedding.npy
```

Cache embeddings first to make head experiments fast.

### Stage 2: Train Conducting Head

Input:

```text
body_embedding
```

Outputs:

```text
tempo_class
bpm_distribution
dynamics
```

Loss:

```python
loss = ce_tempo + kl_bpm_dist + smooth_l1_dynamics
```

### Stage 3: End-to-End Inference

```text
MediaPipe streaming
  -> H36M17 conversion
  -> right-arm mask
  -> MotionBERT-Lite frozen encoder
  -> conducting head
  -> temporal smoothing
  -> MIDI controller
```

## 12. Streaming Runtime

MotionBERT-Lite is not a causal streaming model, so use sliding-window inference.

```text
current v0 camera / MediaPipe Pose: about 15fps
final target camera / MediaPipe Pose: 30fps, or explicit 30fps resampling
MotionBERT-Lite inference: 3~5Hz
current v0 window: 60 frames ~= 4s
current v0 update: every 3 frames ~= 0.2s
final 30fps window: 120 frames = 4s
final 30fps update: every 6 frames = 0.2s
```

Cold start needs one full window. After that, the rolling buffer emits a new estimate every update stride.

Controller smoothing:

```python
bpm = 0.85 * previous_bpm + 0.15 * predicted_bpm
dynamics = 0.90 * previous_dyn + 0.10 * predicted_dyn
```

Do not hard-code this smoothing in the predictor. Runtime must load a policy config so the measured live metrics correspond to the deployed behavior.

Recommended `streaming_laptop.yaml` policy:

```yaml
window_frames: 60
update_stride_frames: 3
warmup_policy: hold_until_full_window
pose_validity_threshold: 0.85
ema_alpha:
  bpm: 0.15
  dynamics: 0.10
switch_threshold:
  tempo: 0.58
  dynamics: 0.60
switch_margin:
  tempo: 0.12
  dynamics: 0.14
confirm_updates:
  tempo: 2
  dynamics: 2
fast_switch_threshold:
  tempo: 0.78
  dynamics: 0.80
hold_on_low_confidence: true
max_hold_seconds: 2.0
```

`right_conducting_stream.py` must parse this YAML and apply:

```text
EMA
confidence threshold
margin threshold
confirm update count
fast switch path
hold on low confidence
max hold timeout
```

Clamp:

```text
BPM v0: 60~120
BPM final: 60~160
dynamics: 0.0~1.0
```

## 13. MIDI Control Mapping

```text
tempo_distribution
  -> expected BPM
  -> MIDI scheduler tempo

dynamics
  -> note velocity scale
  -> CC11 Expression
  -> optional CC7 channel volume
```

Left-hand rule-based controls stay separate:

```text
left wrist zone -> instrument group selection
left fist -> mute
left open / pointing -> cue
```

Do not include left-hand rule signals in deep learning training.

## 14. Metrics

Tempo:

```text
tempo class accuracy
macro F1
BPM MAE
confusion matrix
```

Dynamics:

```text
MAE
Pearson correlation
jitter after smoothing
```

Realtime:

```text
average inference time
end-to-end latency
dropped frame ratio
MIDI control jitter
switch latency after prompt transition
false switch rate during stable segments
```

Aggregation:

```text
window-level metrics
per-take metrics
heldout-session metrics
```

Do not report only mean over windows. Long takes can dominate the metric. The result table must include per-take average rows where possible.

Score table columns:

```text
run_name
model_type
normalization
window_frames
eval_set
fold_or_subject
tempo_acc
tempo_macro_f1
bpm_mae_window
bpm_mae_take
bpm_distribution_kl
dynamics_mae_window
dynamics_mae_take
dynamics_corr
tempo_false_switches_per_min
dynamics_false_switches_per_min
tempo_switch_latency_p90_s
dynamics_switch_latency_p90_s
avg_inference_ms
notes
```

Required rows:

```text
rule_based
handcrafted_feature_ml
motionbert_lite_head
```

## 14.5 Current Risks and Required Reporting

The current workspace dataset is small and likely single-subject. This must be stated in model card and results.

Required limitations:

```text
single-subject or subject-specific if true
only one currently scoreable transition heldout session
session_20260616_215630_eval excluded until relabeled
current v0 data is about 15fps, so 120 frames is about 8s
current v0 tempo classes are 60/80/100/120 only
evaluation folders may contain augmentation artifacts, but scoring must ignore them
cross-subject generalization not proven unless multi-person data is collected
```

Required heldout expansion before strong claims:

```text
stable hold: at least 3 labeled takes
transition: at least 2~3 labeled takes
```

Model card must document:

```text
gain mapping values and source
  small/large class mapping if classification is used in a baseline
  continuous dynamics to velocity/CC11 mapping for final model

checkpoint path
normalization mode
window size and stride
whether MotionBERT backbone is frozen
parameter count of trainable head
```

## 15. Folder Structure

Target implementation repository layout:

```text
Gesture-control-conduct/
  main.py
  src/conductor_demo/
    vision/
      mediapipe_pose.py
      h36m_converter.py
      right_arm_mask.py
      normalizer.py
    data/
      record_right_dataset.py
      extract_pose.py
      convert_h36m.py
      compute_motion_features.py
      make_labels.py
      make_windows.py
      review_annotations.py
      right_dataset.py
    motion/
      motionbert_lite_encoder.py
      right_conducting_head.py
      right_rule_baseline.py
      right_feature_baseline.py
      streaming_inference.py
      controller.py
    train/
      cache_motionbert_lite_features.py
      train_right_conducting_head.py
      evaluate_right_model.py
      evaluate_rule_baseline.py
      train_feature_baseline.py
      benchmark_streaming.py
    music/
      midi_player.py
      midi_controller.py
      wav_player.py
    configs/
      dataset_right_v0.yaml
      model_motionbert_lite_right.yaml
      streaming_laptop.yaml
      augmentation_v0.yaml
    checkpoints/
      motionbert_lite/
      right_conducting_head/
```

For the current MotionBERT workspace, equivalent files should be organized as:

```text
configs/conducting/
  dataset_right_v0.yaml
  model_motionbert_lite_right.yaml
  streaming_laptop.yaml
  augmentation_v0.yaml

lib/data/
  right_conducting_dataset.py

lib/model/
  right_conducting_head.py
  right_feature_baseline.py

lib/inference/
  right_conducting_stream.py

tools/
  cache_motionbert_lite_features.py
  train_right_conducting_head.py
  evaluate_right_model.py
  evaluate_rule_baseline.py
  train_right_feature_baseline.py
  benchmark_right_streaming.py
  export_right_conducting_model.py

docs/exp/
  final_plan_motionbert_lite_conducting_control.md
  mid_presentation_feedback.md
  right_hand_conducting_model_card.md
  right_hand_conducting_scores.md
```

## 16. Execution Phases

### Phase 1: Recording Tool

Implement `record_right_dataset.py`.

Required features:

```text
webcam capture
MediaPipe Pose overlay
BPM prompt
dynamics prompt
raw video save
meta_take.json save
```

### Phase 2: Pose Preprocessing

Implement:

```text
extract_pose.py
convert_h36m.py
right_arm_mask.py
normalizer.py
```

Verify:

```text
pose_33_mediapipe.npy       [T, 33, 3]
pose_17_h36m.npy            [T, 17, 3]
pose_right_h36m_masked.npy  [T, 17, 3]
right_arm_3joints.npy       [T, 3, 3]
```

### Phase 3: Annotation / Windowing

Implement:

```text
compute_motion_features.py
make_labels.py
make_windows.py
review_annotations.py
```

Outputs:

```text
right_rule_features.npy
labels_window.jsonl
quality_report.json
```

### Phase 4: Pilot Training

```text
1-person 40 min dataset
  -> MotionBERT-Lite frozen embedding cache
  -> conducting head training
  -> holdout test evaluation
```

### Phase 5: Final Dataset

```text
5 people x 45~60 min
  -> train/val/test person split
  -> final model training
```

### Phase 6: Realtime Demo

```text
webcam
  -> right-hand model
  -> MIDI tempo/dynamics control
  -> optional left-hand rule instrument selection
```

## 17. Presentation Summary

최종 시스템은 오른손 지휘 동작만 딥러닝 모델의 입력으로 사용한다. MediaPipe Pose로 추출한 33개 body landmark를 H36M 17-joint format으로 변환한 뒤, 오른어깨·오른팔꿈치·오른손목 중심의 right-arm masked sequence를 구성한다. 이 sequence를 MotionBERT-Lite pretrained encoder에 입력하고, encoder는 freeze한 상태에서 tempo distribution과 dynamics 값을 예측하는 lightweight conducting head만 학습한다. 현재 v0 데이터는 약 15fps와 4-class `60/80/100/120 BPM`으로 보고하고, 6-class `60/80/100/120/140/160 BPM`은 추가 데이터 수집 후 final target으로 확장한다. 왼손의 instrument selection, mute, cue는 딥러닝 입력에서 제외하고 rule-based UI control로 분리한다.

## 18. Deliverables

Model:

```text
MotionBERT-Lite frozen encoder
+ right-arm conducting head
```

Input:

```text
MediaPipe Pose 33
  -> H36M17
  -> right shoulder / elbow / wrist centered masked sequence
  -> [B, T, 17, 3]
```

Output:

```text
tempo_class
bpm_distribution
dynamics
```

Dataset:

```text
pilot: 1 person, about 40 min
final: 5 people x 45~60 min
```

Window:

```text
current v0: 60 frames ~= 4s, stride 3 frames ~= 0.2s at about 15fps
current v0 ablation: 120 frames ~= 8s
final 30fps target: 120 frames = 4s, stride 6 frames = 0.2s
```

Annotation:

```text
prompt-driven automatic labels
dynamics corrected by motion radius
quality judged by right-arm valid ratio
```

Augmentation:

```text
train only
jitter / translation / dropout / window offset
temporal stretch and amplitude scaling only with label update
```

Streaming:

```text
current v0 MediaPipe about 15fps
final target MediaPipe 30fps or explicit resampling
MotionBERT-Lite 3~5Hz
smoothing
MIDI tempo/dynamics control
```

Baseline:

```text
existing wrist velocity / motion radius rule-based control
```

## 19. Goal Command

Current verified command for the reproducible v0 goal run:

```bash
bash scripts/run_right_conducting_goal.sh \
  --steps audit,eval,replay,analyze \
  --eval-session dataset/evaluation_transitions/session_20260616_222455_eval \
  --window-frames 60 \
  --stride-frames 3 \
  --normalizations camera \
  --artifact outputs/right_conducting/selected/feature_baseline_live_v0.json \
  --switch-threshold 0.15 \
  --fast-switch-threshold 0.40 \
  --confirm-updates 2 \
  --output-json outputs/right_conducting/right_conducting_goal_run_222455_60f.json \
  --output-md outputs/right_conducting/right_conducting_goal_run_222455_60f.md
```

Verified output artifacts:

```text
outputs/right_conducting/right_conducting_goal_run_222455_60f.json
outputs/right_conducting/right_conducting_goal_run_222455_60f.md
outputs/right_conducting/transition_margin_scores_222455_60f.json
outputs/right_conducting/transition_margin_scores_222455_60f.md
outputs/right_conducting/stream_replay_222455_60f_goal_analysis.json
outputs/right_conducting/stream_replay_222455_60f_goal_analysis.md
```

Current verified steps:

```text
audit
eval
replay
analyze
```

The script supports partial execution:

```text
--steps prepare,audit,eval,replay,analyze
--skip-prepare
--skip-cache
--skip-train
--skip-eval
--skip-export
--models feature_baseline
--folds 0,1,2
--normalizations camera,right_shoulder,right_arm_length
--window-frames 60  # 60 ~= 4s at current 15fps
--stride-frames 3
```

This avoids rerunning every stage during iterative experiments. `cache`, `train`, and `export` remain separate expensive workflows and are not part of the currently verified default goal run.

When `session_20260616_215630_eval` is relabeled:

```bash
bash scripts/run_right_conducting_goal.sh \
  --steps audit,eval,replay,analyze \
  --eval-session dataset/evaluation_transitions/session_20260616_215630_eval \
  --window-frames 60 \
  --stride-frames 3 \
  --normalizations camera \
  --artifact outputs/right_conducting/selected/feature_baseline_live_v0.json \
  --output-json outputs/right_conducting/right_conducting_goal_run_215630_60f.json \
  --output-md outputs/right_conducting/right_conducting_goal_run_215630_60f.md
```
