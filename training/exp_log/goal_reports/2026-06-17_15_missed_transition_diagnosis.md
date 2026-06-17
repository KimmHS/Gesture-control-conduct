# Goal Report 15: Missed 120 -> 80 Transition Diagnosis

## Purpose

Report 14 showed that camera, right_shoulder, 30f, and 60f candidates all miss the second transition in `session_20260616_222455_eval`.

This report diagnoses the failure before changing the model.

Target failure:

```text
true transition: 120 BPM -> 80 BPM
manual timeline time: 54.0s
v0 classes: 60=0, 80=1, 100=2, 120=3
selected fallback: outputs/right_conducting/selected/feature_baseline_live_v0.json
```

## Label Timing

Manual timeline:

```text
0-22s: 100 BPM
22-54s: 120 BPM
54-end: 80 BPM
```

Replay switch timing is later than `54.0s` because window labels are assigned from the window's modal BPM.

| candidate | window | first true class 1 row | first stable all-80 row |
|---|---:|---:|---:|
| selected camera | 60f | 55.9925s | 57.9941s |
| selected camera | 30f | 54.9923s | 55.9925s |

Implication:

```text
The eval session gives very little stable 80 BPM evidence at the tail.
60f has only 11 stable 80 rows.
30f has only 21 stable 80 rows.
```

This explains high variance, but it does not fully explain the miss. Even stable 80 rows are not predicted as class 1.

## Prediction Summary

Artifacts:

```text
outputs/right_conducting/missed_transition_222455_60f_camera_diagnosis.json
outputs/right_conducting/missed_transition_222455_60f_camera_diagnosis.md
outputs/right_conducting/missed_transition_222455_30f_camera_diagnosis.json
outputs/right_conducting/missed_transition_222455_30f_camera_diagnosis.md
```

### 60f Camera

| subset | count | raw predictions | mean dist to 80 | mean dist to 100 | mean dist to 120 | dominant_bpm |
|---|---:|---|---:|---:|---:|---:|
| true 80 all | 21 | `{2: 18, 3: 3}` | 12.3157 | 7.4377 | 9.4574 | 60.0000 |
| true 80 mixed | 10 | `{2: 10}` | 12.3809 | 7.9814 | 11.3608 | 60.0000 |
| true 80 stable | 11 | `{2: 8, 3: 3}` | 12.2564 | 6.9435 | 7.7270 | 60.0000 |

### 30f Camera

| subset | count | raw predictions | mean dist to 80 | mean dist to 100 | mean dist to 120 | dominant_bpm |
|---|---:|---|---:|---:|---:|---:|
| true 80 all | 26 | `{2: 18, 3: 8}` | 16.8070 | 12.4011 | 13.6061 | 60.0000 |
| true 80 mixed | 5 | `{2: 5}` | 13.2189 | 9.2142 | 12.8390 | 60.0000 |
| true 80 stable | 21 | `{2: 13, 3: 8}` | 17.6613 | 13.1599 | 13.7887 | 60.0000 |

Conclusion:

```text
The classifier never emits class 1 in the stable 80 BPM tail.
This is a classifier feature/centroid failure, not only smoothing delay.
```

## Feature-Level Diagnosis

The handcrafted feature artifact includes:

```text
wrist speed / acceleration
shoulder-wrist radius
relative wrist/elbow mean and std
dominant_bpm
```

However, `dominant_bpm` is not separating the tempo classes in the current centroid model.

60f raw centroids:

| class | BPM | dominant_bpm | wrist_speed_mean | rel_wrist_y_std |
|---:|---:|---:|---:|---:|
| 0 | 60 | 60.0710 | 0.3800 | 0.1333 |
| 1 | 80 | 60.0089 | 0.5244 | 0.1606 |
| 2 | 100 | 60.0531 | 0.6420 | 0.1598 |
| 3 | 120 | 61.1368 | 0.8131 | 0.1550 |

30f raw centroids:

| class | BPM | dominant_bpm | wrist_speed_mean | rel_wrist_y_std |
|---:|---:|---:|---:|---:|
| 0 | 60 | 61.2691 | 0.3800 | 0.1214 |
| 1 | 80 | 62.2986 | 0.5246 | 0.1542 |
| 2 | 100 | 61.5955 | 0.6429 | 0.1576 |
| 3 | 120 | 64.2676 | 0.8094 | 0.1528 |

The features that most pull stable 80 windows toward class 2 / 100 BPM are static pose/location features.

60f stable 80, class1-distance minus class2-distance:

| feature | value |
|---|---:|
| `rel_elbow_y_mean` | 2.8356 |
| `rel_wrist_y_mean` | 1.6392 |
| `rel_wrist_x_mean` | 0.6732 |
| `rel_wrist_x_std` | -0.2606 |
| `wrist_speed_max` | 0.2478 |

30f stable 80, class1-distance minus class2-distance:

| feature | value |
|---|---:|
| `rel_elbow_y_mean` | 2.5100 |
| `rel_wrist_y_mean` | 1.1921 |
| `rel_wrist_x_mean` | 0.5060 |
| `wrist_speed_std` | 0.1806 |
| `wrist_speed_max` | 0.1453 |

Positive value means the feature makes class 2 closer than class 1.

Interpretation:

```text
Current fallback is using subject/session posture and arm placement as strong tempo cues.
The FFT-derived dominant_bpm feature collapses near 60 BPM for all classes and is not doing the main tempo work.
The 80 BPM tail has arm placement closer to the training/eval 100 BPM centroid than the 80 BPM centroid.
```

## Root Cause

Primary root cause:

```text
The current centroid fallback is too dependent on absolute/mean pose features.
It generalizes poorly when the performer changes arm placement during a transition.
```

Secondary root cause:

```text
The 80 BPM eval segment is too short and placed at the end of the session.
For 60f windows, stable 80 evidence only appears after 57.99s.
```

Not the primary cause:

```text
Smoothing policy.
```

Reason:

```text
Raw classifier output itself does not reach class 1 in the stable 80 tail.
```

## Decision

Do not tune the smoother further for this failure.

Next model step should remove or downweight static pose means and emphasize temporal motion features:

```text
candidate: pose-invariant feature classifier
drop/downweight:
  rel_wrist_x_mean
  rel_wrist_y_mean
  rel_elbow_x_mean
  rel_elbow_y_mean
keep/emphasize:
  wrist speed statistics
  acceleration statistics
  radius amplitude statistics
  y/std or phase/period features
  confidence/validity
```

Also needed:

```text
collect or relabel more down-transition eval data:
  120 -> 80
  100 -> 80
  120 -> 60
```

Gate:

```text
GO: implement/evaluate pose-invariant feature subset candidate.
NO-GO: more smoothing-only tuning.
NO-GO: claim current fallback handles down-transition live control.
```

## Next Step

Report 16 should run a pose-invariant feature subset classifier.

Minimum acceptance line:

```text
stable heldout tempo_acc should not drop below current 60f camera by more than ~0.03
and raw 120 -> 80 should reach class 1 at least once in session_222455.
```

If the subset candidate fails:

```text
return to data step:
  add heldout down-transition recordings
  then train with transition-focused windows
```
