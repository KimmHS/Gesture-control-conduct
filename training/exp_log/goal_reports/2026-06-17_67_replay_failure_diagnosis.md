# Replay Failure Diagnosis

## Summary

This report adds a replay failure diagnosis step and applies it to the current eval strict chain.

```text
tool: tools/diagnose_motionbert_replay_failures.py
runner step: diagnose-replay
diagnosis json: outputs/right_conducting/current_eval_roots_replay_failure_diagnosis_ext_chain.json
diagnosis md: outputs/right_conducting/current_eval_roots_replay_failure_diagnosis_ext_chain.md
```

The goal is to separate three cases that otherwise look the same in a single score:

- label/scope caveat;
- class collapse;
- true model failure on a stable interval.

## Current Diagnosis

| scope | rows | smoothed tempo_acc | smoothed gain_acc | dominant true tempo | dominant predicted tempo |
|---|---:|---:|---:|---|---|
| all current eval roots | 544 | 0.1691 | 0.9412 | 100:382, 120:146, 80:16 | 80:388, 100:145, 60:11 |
| 222455 eval stress | 258 | 0.2946 | 0.8760 | 120:146, 100:96, 80:16 | 100:129, 80:118, 60:11 |
| 215630 eval transition | 286 | 0.0559 | 1.0000 | 100:286 | 80:270, 100:16 |

Smoothed tempo confusion:

| true \ pred | 60 | 80 | 100 | 120 |
|---|---:|---:|---:|---:|
| 80 | 2 | 14 | 0 | 0 |
| 100 | 9 | 295 | 78 | 0 |
| 120 | 0 | 79 | 67 | 0 |

Longest error runs:

| session | rows | true | predicted | interpretation |
|---|---:|---|---|---|
| 215630 | 263 | 100 | 80 | near-collapsed prediction and label/scope caveat |
| 222455 | 146 | 120 | 80/100 | current model does not recover this 4-beat 120 segment |
| 222455 | 19 | 100 | 80 | early stable segment mismatch |

## Interpretation

The failure is not only transition-margin ambiguity.

`215630` is not usable as final strict score evidence because the true tempo label is constant 100 for all 286 replay windows while the session is still a relabel/scope caveat. It is useful as a warning that the model often collapses toward 80 on out-of-scope eval data.

`222455` is an independent stress session, but it is 4-beat/mixed-timeline and outside the current 2/3-beat fixed-camera P0 heldout target. It still shows a real model weakness: the 120 BPM segment has 0.0 smoothed recall in this stress setting.

## Runner Integration

`tools/run_right_conducting_goal.py` now supports:

```text
step: diagnose-replay
args:
  --replay-diagnosis-output-json
  --replay-diagnosis-output-md
  --replay-diagnosis-top-error-runs
```

The strict chain now runs in this order:

```text
heldout-independence
strict-heldout-scope
replay-selected
diagnose-replay
live-output
live-replay-gate
goal-status
```

## Verification

```bash
python -m py_compile tools/run_right_conducting_goal.py tools/diagnose_motionbert_replay_failures.py
python -m unittest discover -s tests -p 'test_goal_command_cli.py' -v
python -m unittest discover -s tests -p 'test_motionbert_replay_failure_diagnosis.py' -v
```

Result:

```text
py_compile: OK
test_goal_command_cli.py: 30 OK
test_motionbert_replay_failure_diagnosis.py: 3 OK
```

## Next

The next strict pass attempt should use new in-scope 2/3-beat heldout roots. If the same diagnosis appears there, the model needs more 120/100/80 transition coverage or a different temporal representation before claiming live robustness.

