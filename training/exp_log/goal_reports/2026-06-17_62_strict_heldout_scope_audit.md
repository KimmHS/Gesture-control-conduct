# Strict Heldout Scope Audit

## Purpose

Report 61 showed that the available independent heldout stress session fails.
This report separates two different questions:

```text
1. Are the current evaluation roots independent from training?
2. Do those roots cover the current 2/3-beat fixed-camera strict heldout scope?
```

The answer is:

```text
independence: GO
scope coverage: NO_GO
```

## Added Tool

```text
tools/audit_right_conducting_strict_heldout_scope.py
tests/test_strict_heldout_scope_audit.py
```

The tool reads:

```text
docs/exp/right_conducting_required_data_manifest.json
meta.json
manual_timeline.json, if present
```

It ignores:

```text
recommended_augmented_v0/
label_backup*/
```

## Command

```bash
python tools/check_right_conducting_heldout_independence.py \
  --train-manifests outputs/right_conducting/recordings_staged_static80_transitions_manifest.json \
  --heldout-roots dataset/evaluation,dataset/evaluation_transitions \
  --output-json outputs/right_conducting/strict_eval_roots_independence_ext.json \
  --output-md outputs/right_conducting/strict_eval_roots_independence_ext.md

python tools/audit_right_conducting_strict_heldout_scope.py \
  --heldout-roots dataset/evaluation,dataset/evaluation_transitions \
  --independence-json outputs/right_conducting/strict_eval_roots_independence_ext.json \
  --output-json outputs/right_conducting/strict_heldout_scope_audit_ext.json \
  --output-md outputs/right_conducting/strict_heldout_scope_audit_ext.md
```

## Result

| check | value |
|---|---:|
| scope status | NO_GO |
| independence status | GO |
| heldout sessions | 2 |
| P0 required | 8 |
| P0 present | 0 |
| P0 missing | 8 |
| P1 required | 2 |
| P1 present | 0 |
| P2 required | 2 |
| P2 present | 0 |

P0 required cases:

```text
80 static / beat2 / large
80 static / beat2 / small
80 static / beat3 / large
80 static / beat3 / small
120 -> 80 -> 120 / beat2 / large
120 -> 80 -> 120 / beat2 / small
120 -> 80 -> 120 / beat3 / large
120 -> 80 -> 120 / beat3 / small
```

## Current Out-Of-Scope Heldout Sessions

| session | schedule | meter | dynamics | reason |
|---|---|---:|---|---|
| dataset/evaluation/session_20260616_222455_bpm120_beat4_large | `[100, 120, 80]` | mixed | mixed | mixed/missing meter, mixed dynamics, unsupported schedule |
| dataset/evaluation_transitions/session_20260616_215630_bpm100_beat4_large | `[]` | 4 | large | unsupported meter, missing transition schedule |

## Manifest Update

The selected ext manifest now includes:

```text
strict_heldout_scope_evidence:
  json: outputs/right_conducting/strict_heldout_scope_audit_ext.json
  status: NO_GO
  p0_complete: false
```

## Verification

```bash
python -m py_compile tools/audit_right_conducting_strict_heldout_scope.py lib/right_conducting/motionbert_export.py
python -m unittest discover -s tests -p 'test_strict_heldout_scope_audit.py' -v
python -m unittest discover -s tests -p 'test_goal_status.py' -v
```

Result:

```text
py_compile: OK
test_strict_heldout_scope_audit.py: 3 OK
test_goal_status.py: 3 OK
strict scope JSON artifacts: 4 OK
current scope audit: NO_GO / independence GO / P0 0 of 8
```

## Status

```text
live_pilot_status: GO
strict_heldout_status: NO_GO
reason: current evaluation roots are independent but do not cover the in-scope 2/3-beat strict heldout cases.
```

## Next Action

Record a new strict heldout root that is never staged into training. Minimum:

```text
heldout_static_80:
  80 / beat2 / large
  80 / beat2 / small
  80 / beat3 / large
  80 / beat3 / small

heldout_transitions:
  120 -> 80 -> 120 / beat2 / large
  120 -> 80 -> 120 / beat2 / small
  120 -> 80 -> 120 / beat3 / large
  120 -> 80 -> 120 / beat3 / small
```

After capture, first run this scope audit. Only run strict replay/gate after
scope status is `GO`.
