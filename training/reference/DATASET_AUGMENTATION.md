# Dataset Augmentation Methodology

이 문서는 right-hand / right-arm conducting dataset의 pose-level augmentation 기준을 정의한다.
목표는 데이터 부족 문제를 완화하되, tempo와 dynamics label의 의미가 깨지지 않도록 augmentation과 label 정책을 분리하는 것이다.

최종 실험 계획은 [`../exp/final_plan_motionbert_lite_conducting_control.md`](../exp/final_plan_motionbert_lite_conducting_control.md)를 따른다. 현재 v0 데이터는 약 15fps이므로 60-frame window가 약 4초이고, 120-frame window는 약 8초 ablation이다. 기존 `recommended_v0`는 과거 label-preserving only policy이고, 최종 MotionBERT-Lite conducting head 실험에서는 작은 데이터 문제를 줄이기 위해 label-changing augmentation도 v0 실험 후보에 포함한다.

---

## 1. Scope

현재 딥러닝 입력은 오른쪽 상체 skeleton만 사용한다.

```text
input: pose_right_h36m_masked.npy
shape: [T, 17, 3]
valid joints:
  shoulder_center / neck
  left_shoulder        # normalization/reference only
  right_shoulder
  right_elbow
  right_wrist
masked joints:
  confidence = 0
```

왼손 정보는 모델 입력과 augmentation 대상에서 제외한다. 왼쪽 어깨는 왼손 제어 정보가 아니라 scale / body reference로만 유지한다.

---

## 2. Augmentation Principles

Conducting motion에서 tempo는 motion의 주기와 속도, dynamics는 오른손 움직임의 크기와 amplitude에 대응한다. 따라서 augmentation은 두 종류로 나눈다.

| 종류 | 설명 | label 처리 |
|------|------|------------|
| Label-preserving | detector noise, 카메라 위치 변화, 작은 자세 차이를 흉내 낸다. | tempo / dynamics label 유지 |
| Label-changing | motion의 주기나 크기를 의도적으로 바꾼다. | BPM distribution 또는 dynamics target 갱신 |

Validation과 test에는 augmentation을 적용하지 않는다. 원본 recording만 사용한다.

---

## 3. Current Final Policy: right_conducting_v1

최종 실험용 augmentation 정책은 아래 두 종류를 모두 사용한다.

| 종류 | 포함 여부 | 이유 |
|------|-----------|------|
| Label-preserving | 사용 | detector noise, camera variation, small pose variation |
| Label-changing | 사용 | 작은 데이터셋에서 tempo/dynamics 범위를 보강 |

Window size별 output root (`30f/60f/120f`는 FPS가 아니라 window frame count):

```text
data/conducting/right_hand_v0_30f/
  windows/
  manifest.json
  folds.json

data/conducting/right_hand_v0_60f/
  windows/
  manifest.json
  folds.json

data/conducting/right_hand_v0_120f/
  windows/
  manifest.json
  folds.json
```

Window sample shape:

```text
30-frame:  [N, 30, 17, 3]
60-frame:  [N, 60, 17, 3]
120-frame: [N, 120, 17, 3]
```

Label-preserving operations:

```text
window offset
coordinate jitter
smooth motion noise
confidence dropout
translation
scale jitter
small rotation
```

Label-changing operations:

```text
temporal_stretch:
  bpm_aug = bpm_original * stretch_factor
  recompute bpm_distribution
  tempo_class = nearest BPM bin

amplitude_scaling:
  dynamics_aug = clip(dynamics_original * amplitude_scale, 0.0, 1.0)
```

Recommended ranges:

```yaml
temporal_stretch:
  factors: [0.90, 0.95, 1.05, 1.10]
  keep_if_bpm_in_range: [60, 120]
  bins: [60, 80, 100, 120]
amplitude_scaling:
  factors: [0.80, 0.90, 1.10, 1.20]
```

Split rule:

```text
take-level split first
train split only: augmentation
validation/test/heldout: original recordings only
```

## 4. Historical Policy: recommended_v0

현재 프로젝트에서 실제 생성하는 augmentation은 `recommended_v0`이다. 이 버전은 label-preserving augmentation만 사용한다.

Output root:

```text
data/augmented_recommended_v0/
  bpm120/
    session_.../
      pose_right_h36m_masked_windows.npy
      labels_recommended_augmented_windows.jsonl
      meta.json
```

Sample shape:

```text
pose_right_h36m_masked_windows.npy: [N, 120, 17, 3]
```

Label file은 sample별 annotation을 JSONL로 저장한다. 주요 필드는 다음과 같다.

```json
{
  "source_session": "session_20260616_003523_bpm120_beat2",
  "source_start_frame": 0,
  "source_end_frame": 120,
  "augmentation_set": "recommended_v0",
  "operations": [
    "window_start_offset",
    "coordinate_jitter",
    "smooth_motion_noise",
    "confidence_dropout",
    "translation",
    "scale_jitter",
    "small_rotation"
  ],
  "label_preserving": true,
  "bpm_group": "bpm120",
  "tempo_class": 3,
  "bpm_target": 120.0,
  "bpm_distribution": [0.0, 0.05, 0.2, 0.5, 0.2, 0.05],
  "dynamics": 0.62,
  "meter_beats": 2,
  "start_beat_in_bar": 1,
  "end_beat_in_bar": 2,
  "valid_right_shoulder_ratio": 0.99,
  "valid_right_elbow_ratio": 0.96,
  "valid_right_wrist_ratio": 0.98
}
```

---

## 5. recommended_v0 Operations

| Operation | 목적 | 설정 | Label |
|-----------|------|------|-------|
| `window_start_offset` | 같은 take에서 window 시작점을 바꿔 더 많은 sequence를 만든다. | offsets = `0, 2, 4` frames | 유지 |
| `coordinate_jitter` | MediaPipe 좌표 흔들림을 흉내 낸다. | Gaussian sigma = `0.01` | 유지 |
| `smooth_motion_noise` | 시간적으로 이어지는 detector noise를 흉내 낸다. | sigma = `0.005`, alpha = `0.8` | 유지 |
| `confidence_dropout` | wrist / elbow / shoulder가 짧게 사라지는 webcam 상황을 흉내 낸다. | wrist `0.03`, elbow `0.02`, shoulder `0.01`, max `5` frames | 유지 |
| `translation` | 카메라 안 위치 변화와 normalization error를 흉내 낸다. | dx, dy in `[-0.03, 0.03]` | 유지 |
| `scale_jitter` | 카메라 거리와 body scale 차이를 약하게 흉내 낸다. | scale in `[0.95, 1.05]` | 유지 |
| `small_rotation` | 상체 기울기와 작은 카메라 각도 차이를 흉내 낸다. | degree in `[-5, 5]` | 유지 |

이 세트는 tempo 주기와 dynamics amplitude의 의미를 바꾸지 않는 범위로 제한한다.

---

## 6. Excluded From recommended_v0

현재 v0에서는 아래 augmentation을 사용하지 않는다.

| Operation | 제외 이유 |
|-----------|-----------|
| `temporal_stretch` | motion 주기가 바뀌므로 BPM label과 distribution을 함께 수정해야 한다. |
| `amplitude_scaling` | motion amplitude가 바뀌므로 dynamics target을 함께 수정해야 한다. |
| `horizontal_flip` | 오른손 지휘가 왼손 지휘로 바뀌어 프로젝트의 오른손/왼손 역할 분리와 충돌한다. |

---

## 7. Label-Changing Augmentation Details

최종 실험에서는 label-changing augmentation을 별도 버전으로 미루지 않고, train split에만 적용하는 후보로 둔다.

### Temporal stretch

```text
s > 1: motion faster, BPM increases
s < 1: motion slower, BPM decreases

bpm_aug = bpm_original * s
tempo_class = nearest BPM bin
bpm_distribution = recompute from bpm_aug
```

초기 권장 범위는 `s in [0.95, 1.05]`이다.

### Amplitude scaling

```text
p_aug[t] = origin + a * (p[t] - origin)
dynamics_aug = clip(dynamics_original * a, 0.0, 1.0)
```

초기 권장 범위는 `a in [0.80, 1.20]`이다. dynamics calibration 기준이 생기면 wrist radius를 calibration range로 다시 normalize한다.

---

## 8. Rule-Based Dynamics Baseline

Dynamics는 `small`과 `large` recording을 기준으로 rule-based baseline을 함께 사용한다. 이 baseline은 모델 출력의 fallback, smoothing 기준, 또는 regression target sanity check로 쓸 수 있다.

사용 artifact:

```text
right_rule_features.npy
```

Feature order:

```text
wrist_vx
wrist_vy
wrist_speed
shoulder_wrist_radius
elbow_angle_rad
right_arm_valid
```

기본 계산:

```text
amplitude = shoulder_wrist_radius 또는 최근 wrist span
d_raw = clip((amplitude - small_ref) / (large_ref - small_ref), 0.0, 1.0)
d_smooth[t] = d_smooth[t-1] + alpha * (d_raw[t] - d_smooth[t-1])
```

권장값:

```text
alpha = 0.15 ~ 0.25
deadband = 0.02
```

`small_ref`는 small recording에서의 median amplitude, `large_ref`는 large recording에서의 median 또는 high-percentile amplitude로 둔다. `right_arm_valid = 0`인 프레임은 smoothing 상태를 유지하거나 이전 값을 사용한다.

이 방식은 dynamics가 discrete class가 아니라 연속적인 intensity처럼 동작하게 만든다. 따라서 v0에서는 `small`과 `large`만 촬영하고, 중간값은 rule-based normalization과 smoothing으로 처리한다.

---

## 9. Train / Validation / Test Rule

Augmentation은 split 이후 train split에만 적용한다.

```text
raw recording take
  -> pose extraction
  -> MediaPipe33 to H36M17
  -> normalization / right-arm masking
  -> take-level train / validation / test split
  -> train only: augmentation
  -> MotionBERT-Lite embedding cache
  -> tempo / dynamics head training
```

같은 원본 take에서 파생된 augmentation sample이 train과 validation/test에 동시에 들어가면 validation 성능이 과대평가된다. 따라서 split 단위는 frame이나 window가 아니라 recording take 단위로 둔다.

---

## 10. Reporting Text

보고서나 발표에는 다음 문장을 사용할 수 있다.

```text
데이터 부족 문제를 완화하기 위해 right-arm skeleton sequence에 대해 pose-level augmentation을 적용한다.
구체적으로 window start offset, coordinate jitter, smooth motion noise, confidence dropout,
small translation, scale, rotation을 사용하여 MediaPipe tracking noise와 카메라 위치 변화를 시뮬레이션한다.
Tempo와 dynamics의 의미를 보존하는 augmentation은 label을 유지하고,
temporal stretch와 amplitude scaling처럼 motion의 주기나 크기를 바꾸는 augmentation은
각각 BPM distribution과 dynamics target을 함께 갱신한다.
Validation과 test에는 augmentation을 적용하지 않고 원본 recording만 사용한다.
```
