# Report 46 - Remaining Experiments And Report Contents

## Scope

이 문서는 앞으로 남은 실험과 최종 리포트에 들어갈 내용을 정리한다.

현재 결론:

```text
current selected live model: feature_baseline_live_v0
MotionBERT replacement: NO_GO
main blocker: transition/stable 80 BPM robustness
current readiness: WAIT_FOR_STATIC_80_DATA
```

## 1. 지금 바로 가능한 진단 실험

추가 데이터 없이 현재 `dataset/transitions`와 기존 eval set으로 확인할 수 있는 실험이다.

| order | experiment | 목적 | pass / interpretation | output |
|---:|---|---|---|---|
| 1 | middle-only 80 crop score | 전환 지점이 아닌 순수 80 구간에서도 80을 못 맞히는지 확인 | 80 recall이 계속 0이면 모델/feature 문제 | `middle_only_80_score.*` |
| 2 | window anchor comparison | window label 기준을 start/center/end로 바꿨을 때 score 변화 확인 | center/end에서 회복되면 alignment 문제 | `window_anchor_score.*` |
| 3 | window offset sweep | window를 앞/뒤로 이동했을 때 score 변화 확인 | 특정 offset에서 회복되면 latency/alignment 문제 | `window_offset_sweep.*` |
| 4 | true/pred timeline plot | 중간 80 구간에서 예측이 어떤 class로 가는지 시각화 | 80 대신 100/120으로 고정되는지 확인 | `true_pred_timeline.*` |
| 5 | confusion matrix by segment | source / middle / return 구간별 confusion 확인 | middle segment failure를 분리 | `segment_confusion.*` |

### 1.1 Middle-Only 80 Crop

질문:

```text
중간 구간은 무조건 80인데, 전환 근처를 제외한 순수 80 window에서도 모델이 80을 못 맞히는가?
```

권장 crop:

```text
transition schedule: 0s source, 15s target 80, 30s source
middle-only 80 region: roughly 18s ~ 27s
```

해석:

| 결과 | 의미 |
|---|---|
| 80 recall still 0 | window ambiguity가 아니라 stable 80 representation failure |
| 80 recall recovers | transition/window labeling 또는 smoothing 문제가 큼 |

### 1.2 Window Anchor / Offset

아직 명시적으로 하지 않은 실험:

| setting | 의미 |
|---|---|
| start-label | window 시작 frame의 BPM 기준 |
| center-label | window 중앙 frame의 BPM 기준 |
| end-label | causal/live 관점에서 window 끝 frame의 BPM 기준 |
| offset -2s/-1s/0/+1s/+2s | 예측 window를 label 기준보다 앞/뒤로 이동 |

이 실험은 `80 recall = 0`이 단순한 window 기준 문제인지 확인하기 위한 진단이다.

## 2. 추가 데이터가 필요한 실험

현재 broad 5-GPU sweep은 막아둔다. 먼저 P0 fixed-camera 80 static devset이 필요하다.

### 2.1 P0 데이터 수집

필수 static 80 data:

| BPM | meter | dynamics | variant |
|---:|---:|---|---|
| 80 | 2 | large | fixed camera high arm |
| 80 | 2 | small | fixed camera high arm |
| 80 | 3 | large | fixed camera low arm |
| 80 | 3 | small | fixed camera low arm |
| 80 | 4 | large | fixed camera neutral arm |
| 80 | 4 | small | fixed camera neutral arm |

현재 이미 충족된 P0 transition:

| sequence | required cases | status |
|---|---:|---|
| 120 -> 80 -> 120 | 4 | present in `dataset/transitions` |

### 2.2 Devset Coverage Audit

목적:

```text
필수 P0 case가 모두 들어왔는지 확인한다.
```

Pass line:

```text
p0_complete = true
```

Output:

```text
outputs/right_conducting/devset_edge_case_audit.json
outputs/right_conducting/devset_edge_case_audit.md
outputs/right_conducting/devset_missing_checklist.json
outputs/right_conducting/devset_missing_checklist.md
```

### 2.3 Static 80 Score

목적:

```text
transition ambiguity 없이 stable 80 BPM 자체를 맞히는지 확인한다.
```

Target:

| metric | target |
|---|---:|
| static 80 recall | >= 0.60 |
| gain accuracy | >= 0.80 |

Output:

```text
outputs/right_conducting/motionbert_devset_static_score_60f.json
outputs/right_conducting/motionbert_devset_static_score_60f.md
```

### 2.4 Transition Stress Score

목적:

```text
120 -> 80 -> 120에서 margin 3s 이후 stable 80 tail을 맞히는지 확인한다.
```

Target:

| metric | target |
|---|---:|
| transition 80 recall at margin 3s | >= 0.50 |
| gain accuracy | >= 0.80 |

Output:

```text
outputs/right_conducting/motionbert_devset_transition_score_60f.json
outputs/right_conducting/motionbert_devset_transition_score_60f.md
```

### 2.5 Devset Gate

목적:

```text
coverage, static score, transition score를 묶어서 다음 sweep 가능 여부를 결정한다.
```

Pass line:

```text
devset gate = GO
```

Output:

```text
outputs/right_conducting/motionbert_devset_gate_60f.json
outputs/right_conducting/motionbert_devset_gate_60f.md
```

## 3. Devset Gate 이후 모델 실험

Devset gate가 GO일 때만 실행한다.

| order | experiment | 목적 | pass line |
|---:|---|---|---|
| 1 | 5-GPU window sweep | 30/45/60/90/120 또는 확장 window 비교 | regular gate GO + devset gate GO |
| 2 | MotionBERT candidate selection | best candidate 선택 | selected candidate exists |
| 3 | export selected bundle | live bundle 생성 | smoke pass |
| 4 | replay selected bundle | live-style replay 검증 | false switch / delay fallback 이하 |

Regular score gate:

| metric | target |
|---|---:|
| CV tempo accuracy | >= 0.70 |
| CV gain accuracy | >= 0.95 |
| transition tempo accuracy | >= 0.60 |
| transition BPM MAE | <= 10.0 |
| transition gain accuracy | >= 0.80 |
| tempo 80 recall | >= 0.50 |
| tempo 120 recall | >= 0.50 |

## 4. 실패 시 분기

| failed experiment | 의미 | 다음 액션 |
|---|---|---|
| middle-only 80 crop fails | stable 80 representation failure | static 80 data 우선, feature/model 구조 점검 |
| window anchor/offset만 통과 | alignment/latency 문제 | end-label/center-label scoring 및 streaming policy 조정 |
| static 80 score fails | transition 문제가 아니라 80 class 자체 문제 | normalization, temporal feature, beat-phase auxiliary target 검토 |
| static 80 OK, transition 80 fails | transition adaptation 문제 | shorter window, causal replay, smoothing policy 점검 |
| gain acc fails | dynamics label/calibration 문제 | continuous dynamics threshold 및 amplitude 분포 점검 |
| CV GO but devset NO_GO | domain cue overfit | MotionBERT export 금지, 데이터/입력 설계 보강 |

## 5. 최종 리포트에 들어갈 내용

최종 제출 형식:

```text
docs/exp/final_report_submission_format.md
```

포함할 큰 항목:

| section | 들어갈 내용 |
|---|---|
| Task 설명 | 오른손 pose 기반 MIDI tempo/dynamics 제어 |
| Demo | 영상, overlay, raw/smoothed prediction |
| Method | rule-based baseline, MotionBERT-Lite branch |
| Dataset | stable train, heldout eval, transition stress, final eval protocol |
| Model Structure | input tensor, backbone, conducting head, window sizes |
| Challenge | transition ambiguity, stable 80 failure, class imbalance |
| Result | metric, target score, model comparison, margin/window/per-class tables |
| Graph | window score, margin score, confusion matrix, timeline, heatmap |

필수 result tables:

| table | status |
|---|---|
| overall model comparison | required |
| window size sweep | required |
| transition margin sweep | required |
| per-class tempo precision/recall/F1 | required |
| per-class gain precision/recall/F1 | required |
| streaming replay raw/smoothed | required |

필수 graphs:

| graph | status |
|---|---|
| window_size_vs_score | required |
| margin_vs_score | required |
| confusion_matrix | required |
| per_class_f1_bar | required |
| true_pred_timeline | required |
| gain_timeline | recommended |
| per_session_heatmap | recommended |

## 6. 현재 우선순위

```text
P0: run middle-only 80 crop + window anchor/offset diagnostics on existing data
P0: collect fixed-camera 80 BPM static variants under dataset/static_variants_80
P0: rerun devset-audit and devset-missing-checklist
P0: run static 80 score and transition stress score
P0: run devset gate
P1: only if gate GO, run broad 5-GPU sweep
P1: only if selection GO, export and replay selected bundle
```

Current policy:

```text
Do not export a MotionBERT replacement until both regular score gate and devset gate pass.
Keep feature_baseline_live_v0 as selected fallback for now.
```

