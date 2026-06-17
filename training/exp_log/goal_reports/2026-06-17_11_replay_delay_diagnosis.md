# Goal Report 11 - Replay Delay Diagnosis

## Status

Current stage:

```text
selected live fallback replay: diagnosed
raw classifier delay vs smoothing delay: separated
second eval 215630: still excluded until relabel
```

Current decision:

```text
The main live tempo delay is not only the smoother.
The raw fallback classifier itself changes late or misses a target switch.
```

## Why This Step

Goal Report 10 selected a conservative stream policy:

```text
switch_threshold: 0.15
fast_switch_threshold: 0.40
confirm_updates: 2
false_switches_per_min: 4.2811
switch_delay_mean_s: 7.6037
```

That number mixes two sources:

```text
1. raw model/fallback delay
2. smoothing / confirmation delay
```

This report separates them.

## Code Change

Added reusable replay-delay analysis:

```text
lib/right_conducting/stream_replay.py
  compute_switch_delay_breakdown
  summarize_switch_delay_breakdown

tools/analyze_right_conducting_replay.py
tests/test_analyze_stream_replay_cli.py
tests/test_stream_replay.py
```

## Command

```bash
python tools/analyze_right_conducting_replay.py \
  --rows outputs/right_conducting/stream_replay_222455_60f_tuned_rows.jsonl \
  --output-json outputs/right_conducting/stream_replay_222455_60f_tuned_analysis.json \
  --output-md outputs/right_conducting/stream_replay_222455_60f_tuned_analysis.md
```

## Artifacts

```text
outputs/right_conducting/stream_replay_222455_60f_tuned_analysis.json
outputs/right_conducting/stream_replay_222455_60f_tuned_analysis.md
```

## Result

v0 tempo class map:

```text
0: 60 BPM
1: 80 BPM
2: 100 BPM
3: 120 BPM
```

Summary:

```text
switch_count: 2
raw_reached_count: 1
raw_missed_count: 1
smoothed_reached_count: 1
smoothed_missed_count: 1
raw_delay_mean_s: 6.6031
smoothed_delay_mean_s: 7.6037
smoothing_extra_delay_mean_s: 1.0006
```

Switch table:

| switch_time_s | transition | raw_first_time_s | raw_delay_s | smoothed_first_time_s | smoothed_delay_s | smoothing_extra_delay_s |
|---:|---|---:|---:|---:|---:|---:|
| 24.1772 | 100 -> 120 BPM | 30.7804 | 6.6031 | 31.7810 | 7.6037 | 1.0006 |
| 55.9925 | 120 -> 80 BPM | NA | NA | NA | NA | NA |

## Interpretation

The first switch shows:

```text
raw classifier delay: 6.6031s
smoother additional delay: 1.0006s
```

So reducing only `confirm_updates` or EMA will not solve the current live delay.

The second switch shows:

```text
target: 80 BPM
raw classifier: never reaches 80 BPM after the true switch
smoothed output: also never reaches 80 BPM
```

This is a model/feature/generalization issue, not a controller-only issue.

## Current Gate

Pass line for live fallback:

```text
false_switches_per_min <= 5
switch_delay_p90_s <= 3
raw_missed_switch_count = 0
```

Current status:

```text
false_switches_per_min: pass
switch_delay_p90_s: fail
raw_missed_switch_count: fail
```

## Next Step

The next useful work should target the classifier side before more smoother tuning:

```text
1. relabel session_20260616_215630_eval and rerun the same replay diagnosis
2. compare normalization modes on heldout transition
3. add temporal_stretch / amplitude_scaling to train-only augmentation for transition robustness
4. train a temporal head that preserves motion frequency instead of relying on window-level centroids
```

Until another eval is labeled, treat this as a single-session diagnosis only.
