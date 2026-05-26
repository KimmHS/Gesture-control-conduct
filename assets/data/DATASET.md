# Gesture Conducting Dataset

지휘 제스처 기반 템포 추론 모델 학습용 데이터셋입니다.  
메트로놈에 맞춰 지휘하는 동안 손 랜드마크와 다이나믹스를 프레임 단위로 녹화합니다.

---

## 녹화 환경

| 항목 | 값 |
|------|----|
| 카메라 해상도 | 1280 × 720 |
| 샘플링 레이트 | ~15 FPS (MacBook 웹캠 기준) |
| 손 감지 모델 | MediaPipe HandLandmarker (float16) |
| 좌표계 | 프레임 크기 기준 정규화 (0.0 ~ 1.0) |
| 손목 스무딩 | 지수 이동 평균 (α = 0.2) |
| 다이나믹스 윈도우 | 최근 0.6초 |

---

## 파일 형식

```
data/recordings/session_YYYYMMDD_HHMMSS_bpm{BPM:03d}.csv
```

- 파일명에 레이블(BPM)이 포함됩니다.
- 헤더 1행 + 데이터 N행 (프레임당 1행)
- 손 미감지 프레임은 랜드마크/wrist 컬럼이 `-1`

---

## 컬럼 명세 (56개)

### 메타 (3개)

| 인덱스 | 컬럼명 | 타입 | 설명 |
|--------|--------|------|------|
| 0 | `timestamp` | float | 프레임 시각 (단조 시계, 초) |
| 1 | `bpm` | float | **레이블** — 메트로놈 BPM (40 ~ 220) |
| 2 | `beat_phase` | float | 현재 박자 내 위치 (0.0 = 박자 시작, 1.0 = 다음 박자 직전) |

### 랜드마크 (42개)

| 인덱스 | 컬럼명 | 타입 | 설명 |
|--------|--------|------|------|
| 3 ~ 44 | `lm_{i}_x`, `lm_{i}_y` | float | 랜드마크 i의 정규화 좌표 (i = 0 ~ 20) |

MediaPipe 손 랜드마크 인덱스:

```
lm_0          손목 (Wrist)
lm_1  ~ lm_4  엄지  (CMC → MCP → IP → Tip)
lm_5  ~ lm_8  검지  (MCP → PIP → DIP → Tip)
lm_9  ~ lm_12 중지
lm_13 ~ lm_16 약지
lm_17 ~ lm_20 새끼손가락
```

손 미감지 시 모든 랜드마크 컬럼 = `-1`

### 손목 (4개)

| 인덱스 | 컬럼명 | 타입 | 설명 |
|--------|--------|------|------|
| 45 | `wrist_x` | float | EMA 스무딩 손목 X (정규화) |
| 46 | `wrist_y` | float | EMA 스무딩 손목 Y (정규화) |
| 47 | `raw_wrist_x` | float | 원시 손목 X (정규화) |
| 48 | `raw_wrist_y` | float | 원시 손목 Y (정규화) |

### 손 상태 (3개)

| 인덱스 | 컬럼명 | 타입 | 설명 |
|--------|--------|------|------|
| 49 | `hand_scale_px` | float | 손 크기 (손가락 간 거리 평균, px) — 카메라 거리 보정용 |
| 50 | `confidence` | float | 손 감지 신뢰도 (0.0 ~ 1.0) |
| 51 | `tracking_mode` | str | `live` / `hold` / `lost` |

`tracking_mode` 값:

| 값 | 의미 |
|----|------|
| `live` | 현재 프레임에서 손 감지 성공 |
| `hold` | 일시적 손실 — 마지막 위치 유지 (최대 0.75초) |
| `lost` | 손 감지 실패 |

### 다이나믹스 (4개)

| 인덱스 | 컬럼명 | 타입 | 설명 |
|--------|--------|------|------|
| 52 | `dynamics_intensity` | float | 스무딩된 지휘 강도 (0.0 ~ 1.0) |
| 53 | `dynamics_raw_intensity` | float | 스무딩 전 원시 강도 |
| 54 | `dynamics_span_px` | float | 최근 0.6초 손목 이동 범위 (px) |
| 55 | `dynamics_reference_span_px` | float | 정규화 기준값 (캘리브레이션 기반) |

---

## 샘플 데이터

```
timestamp,       bpm,   beat_phase, lm_0_x,  lm_0_y,  ..., wrist_x, wrist_y, hand_scale_px, confidence, tracking_mode, dynamics_intensity, dynamics_span_px
227478.097009,   120.0, 0.0261,     0.63281, 0.66528,  ..., 0.63600, 0.57681, 94.76,         0.8874,     live,          0.1073,             40.32
```

---

## 모델 학습 가이드

### 입력 / 출력

```
입력 (X) : lm_0~20 (42) + wrist_x/y (2) + dynamics_span_px (1) = 45개 피처 × N프레임 시퀀스
출력 (y) : bpm  (회귀) 또는 BPM 구간 클래스 (분류)
```

### 추천 피처 조합

| 목적 | 피처 |
|------|------|
| 기본 | `wrist_x`, `wrist_y`, `dynamics_span_px` |
| 고정밀 | 위 + `lm_0~20` 전체 |
| 카메라 거리 불변 | 랜드마크를 `hand_scale_px`로 정규화 |

### `beat_phase` 활용

`beat_phase`는 예측 레이블이 아닌 **보조 감독 신호**입니다.  
BPM을 알면 beat_phase의 주기를 역산할 수 있으므로, 멀티태스크 학습(BPM + beat_phase 동시 예측)에 활용할 수 있습니다.

### 전처리 권장사항

- `tracking_mode == 'lost'` 프레임 제거 또는 마스킹
- 랜드마크 `-1` 구간 보간 또는 시퀀스 분할
- 세션 간 `hand_scale_px` 기준 좌표 정규화 (사용자별 손 크기 차이 제거)
- 슬라이딩 윈도우로 시퀀스 구성 (예: 30프레임 = 약 2초)

---

## 녹화 도구

```bash
conda activate asr
python record_data.py
```

| 키 | 동작 |
|----|------|
| `R` | 녹화 시작 / 중지 |
| `C` | 캘리브레이션 |
| `]` / `[` | BPM +5 / -5 |
| `Q` / `Esc` | 종료 |
