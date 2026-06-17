# Goal Report 01: Prompt Analysis and Augmentation Survey

Date: 2026-06-16  
Scope: goal 시작점 정리. 아직 training/evaluation score는 생성하지 않았다.

## 1. Prompt Analysis

사용자 목표를 실행 가능한 요구사항으로 나누면 아래와 같다.

| 요구 | 현재 해석 | 증거/파일 |
|---|---|---|
| 실시간 handmark dataset 입력 | streaming 환경에서 pose/keypoint sequence를 window로 받아 추론 | `docs/exp/final_plan_motionbert_lite_conducting_control.md` |
| tempo/gain classification | current v0는 tempo `60/80/100/120`, gain은 `small/large` 또는 continuous dynamics를 classification/report용 binning | `docs/reference/CURRENT_DATA.md` |
| 안정적이되 빨리 바뀌는 출력 | EMA + threshold + confirm update + fast switch policy 필요 | final plan `Streaming Runtime` |
| 데이터 부족 해결부터 시작 | augmentation, soft label, confidence weighting, baseline 순으로 ROI 정리 | `docs/exp/dataset_shortage_action_plan.md` |
| 논문/기술블로그 survey 기반 | time-series/skeleton augmentation 근거를 먼저 정리 | 아래 Section 3 |
| 단계별 수행과 후퇴선 | 각 stage마다 pass/fail gate를 두고 막히면 이전 단계로 내려감 | 아래 Section 5 |
| 매번 새 리포트 | `docs/exp/goal_reports/`에 turn별 report를 누적 | 이 파일 |

현재 objective의 최종 완료 조건은 아직 멀다. 이 report는 첫 단계인 prompt analysis와 augmentation survey만 완료 대상으로 둔다.

## 2. Current Workspace Facts

현재 repo 기준 v0 실험 전제:

```text
training data: dataset/recordings.zip
training takes: 24
subject: single-subject 추정
fps: about 15
tempo bins: 60 / 80 / 100 / 120
default window: 60 frames ~= 4s
120-frame window: ~= 8s ablation
scoreable transition eval: dataset/evaluation_transitions/session_20260616_222455_eval
pending relabel eval: dataset/evaluation_transitions/session_20260616_215630_eval
```

따라서 current v0에서 바로 6-class `60/80/100/120/140/160` 결과를 주장하면 안 된다. 6-class는 추가 데이터 이후 final target이다.

## 3. Survey Notes

### 3.1 Time-Series Augmentation

Time-series augmentation survey는 augmentation이 label을 유지하려면 temporal dependency와 task 특성을 보존해야 한다고 정리한다. 기본 time-domain 방법은 cropping, flipping, jittering 등에서 시작하지만, multivariate sequence에서는 변수 간 dynamics를 깨지 않는지 확인해야 한다. Source: [IJCAI 2021 survey](https://www.ijcai.org/proceedings/2021/0631.pdf).

실무 라이브러리 `tsai`도 smooth noise, magnitude warp, time warp, window warp, scaling을 time-series transform으로 제공한다. 우리 문제에 직접 대응시키면 coordinate jitter, smooth motion noise, temporal stretch, amplitude scaling, window crop/offset이 된다. Source: [tsai time-series transforms](https://timeseriesai.github.io/tsai/data.transforms.html).

Uchida lab의 time-series augmentation reference는 jittering, rotation, magnitude warping, time warping, window slicing, DTW-based averaging 등을 정리한다. 우리 v0에서는 DTW/generative 계열보다 deterministic label update가 가능한 jitter/scale/time stretch를 먼저 쓰는 것이 안전하다. Source: [time_series_augmentation methods](https://github.com/uchidalab/time_series_augmentation/blob/master/docs/AugmentationMethods.md).

### 3.2 Skeleton / Pose Augmentation

Skeleton action recognition 쪽에서는 spatial augmentation과 temporal augmentation을 분리해 다룬다. conducting pose sequence에서는 spatial augmentation이 camera/person variation, temporal augmentation이 BPM 변화와 연결된다. Source: [Enhancing Human Action Recognition with 3D Skeleton Data](https://www.mdpi.com/2079-9292/13/4/747).

Real-world skeleton recognition에서는 pose estimator 오류를 닮은 augmentation이 실제 환경 robustness에 도움이 된다는 방향이 있다. 우리 v0의 confidence dropout, joint masking, coordinate jitter는 MediaPipe tracking noise를 흉내 내기 위한 항목으로 유지할 가치가 있다. Source: [WACV 2024 workshop paper](https://openaccess.thecvf.com/content/WACV2024W/RWS/html/Cormier_Enhancing_Skeleton-Based_Action_Recognition_in_Real-World_Scenarios_Through_Realistic_Data_WACVW_2024_paper.html).

Self-supervised skeleton literature도 joint masking / temporal masking을 많이 쓴다. 하지만 지금 goal의 첫 병목은 supervised v0 score이므로, masked self-supervised pretraining은 A1/A2/A4 이후로 둔다.

### 3.3 MotionBERT and MediaPipe

MotionBERT는 noisy partial 2D observation에서 3D motion을 복원하도록 pretrained motion encoder를 학습하고, downstream task로 transfer하는 구조다. 이 프로젝트에서 frozen MotionBERT-Lite encoder + 작은 conducting head를 쓰는 선택과 맞다. Sources: [MotionBERT project](https://motionbert.github.io/), [ICCV 2023 paper](https://openaccess.thecvf.com/content/ICCV2023/papers/Zhu_MotionBERT_A_Unified_Perspective_on_Learning_Human_Motion_Representations_ICCV_2023_paper.pdf).

MediaPipe Pose Landmarker는 image/video/live feed에서 body landmarks를 image/world coordinates로 출력한다. 따라서 final stream 입력은 MediaPipe output을 H36M17로 변환하는 전처리 안정성이 먼저 검증되어야 한다. Source: [Google AI Edge Pose Landmarker](https://developers.google.com/edge/mediapipe/solutions/vision/pose_landmarker).

## 4. Augmentation Decision for v0

현재 데이터가 작기 때문에 augmentation은 v0에 넣는다. 단, heldout/eval에는 절대 넣지 않는다.

### Keep label

| Augmentation | 이유 | v0 range |
|---|---|---|
| window offset | 같은 take 안 시작점 다양화 | `+-5 frames` |
| coordinate jitter | detector noise | `sigma 0.005~0.01` |
| smooth motion noise | MediaPipe temporal noise | `sigma 0.003~0.005` |
| confidence dropout | joint miss robustness | wrist/elbow/shoulder short dropout |
| small translation/rotation/scale | camera/person placement variation | small only |

### Change label

| Augmentation | label update | v0 policy |
|---|---|---|
| temporal stretch | `bpm_aug = bpm / stretch_factor` 또는 실제 구현 기준으로 정의 고정 후 distribution recompute | keep if nearest bin in `60/80/100/120` |
| amplitude scaling | `dynamics_aug = clip(dynamics * scale, 0, 1)` | gain class threshold는 report에 명시 |

중요: temporal stretch의 수식은 구현 전에 한 번만 고정해야 한다. “sequence를 시간축으로 늘림”을 slower motion으로 볼지, resampling factor를 inverse로 정의할지에 따라 `bpm_aug` 방향이 바뀐다. 구현 코드와 report가 같은 정의를 써야 한다.

## 5. Step Plan and Gates

### Stage 0: Evidence and dataset audit

Goal:

```text
recordings.zip unpack/read
train sessions count
label distribution
eval artifact exclusion rule
fps/window consistency
```

Pass line:

```text
manifest has 24 train takes
tempo bins are only 60/80/100/120
eval scoring path ignores augmentation files
```

Fallback:

```text
if labels are inconsistent, stop training and regenerate labels/windows
```

### Stage 1: Augmentation expansion

Goal:

```text
make train-only augmented windows
support 60-frame default and 120-frame ablation
emit manifest with source_take and aug_type
```

Pass line:

```text
augmented train samples >= 5x original train windows
validation/eval sample count from augmented sources = 0
label distribution after temporal stretch remains inside v0 bins
```

Fallback:

```text
if label-changing augmentation causes impossible labels, disable temporal stretch and keep label-preserving only
```

### Stage 2: Baselines

Goal:

```text
rule baseline
hand-crafted feature ML baseline
```

Pass line:

```text
score table has at least rule_based and feature_baseline rows
metrics include tempo_acc, bpm_mae, gain_acc or dynamics_mae
```

Fallback:

```text
if feature baseline is unstable, report rule baseline only and continue to MotionBERT head
```

### Stage 3: MotionBERT-Lite conducting head

Goal:

```text
frozen checkpoint load
right-arm pooling head
soft-label KL tempo loss
gain/dynamics head
```

Pass line:

```text
smoke test passes for T=60 and T=120
training produces checkpoint + config + score row
```

Fallback:

```text
if MotionBERT shape/checkpoint blocks, train small temporal head on H36M17 windows while preserving same output contract
```

### Stage 4: Streaming policy evaluation

Goal:

```text
offline replay of eval windows
EMA / threshold / confirm update policy
false switches and switch latency metrics
```

Pass line:

```text
stable hold data exists or report explicitly says transition-only early check
eval uses labels_window.jsonl only
```

Fallback:

```text
if transition labels are ambiguous, report only classification metrics and skip switch latency claim
```

### Stage 5: Export

Goal:

```text
model params
model structure/config
streaming policy yaml
score table
model card
```

Pass line:

```text
one command can reproduce prepare/train/eval/export
artifacts are listed in model card
```

Fallback:

```text
if full goal command is too slow, require partial flags for prepare/train/eval/export
```

## 6. First Implementation Priority

다음 작업 순서는 아래로 고정한다.

1. Dataset audit script/report
2. Train-only augmentation generator
3. Rule baseline score
4. Feature baseline score
5. MotionBERT-Lite smoke test
6. MotionBERT-Lite head training
7. Offline streaming replay score
8. Export/model card/goal command

GPU 5장은 Stage 3 이후 fold/model sweep에 쓴다. Stage 0~2는 CPU/단일 GPU로 병목을 먼저 제거한다.

## 7. Next Report

다음 report는 `Goal Report 02: Dataset Audit`로 만든다.

Required contents:

```text
recordings.zip structure
number of sessions/takes
fps estimate per take if available
window counts for 60f/120f
tempo/gain label distribution
eval sessions and excluded augmentation artifacts
go/no-go for augmentation generation
```
