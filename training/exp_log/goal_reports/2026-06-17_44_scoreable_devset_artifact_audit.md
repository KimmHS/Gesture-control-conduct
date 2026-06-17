# Report 44 - Scoreable Devset Artifact Audit

## Scope

The previous devset coverage audit matched cases from metadata only. That was not enough for scoring, because a session with only `meta.json` could be counted as present even though evaluation would later fail.

This report updates the devset audit so a case is present only when:

```text
metadata matches the required case
AND required original score artifacts exist
```

## Required Original Artifacts

The source manifest now declares:

```text
docs/exp/right_conducting_required_data_manifest.json
```

Required per scoreable session:

```text
meta.json
labels_frame.jsonl
labels_window.jsonl
pose_right_h36m_masked.npy
right_rule_features.npy
```

Eval-local augmentation remains excluded from scoring:

```text
recommended_augmented_v0/
labels_tempo_augmented_15f.jsonl
tempo_augmented_15f.npy
```

## Code Changes

Updated:

```text
tools/audit_right_conducting_devset_edges.py
tests/test_devset_edge_audit.py
docs/exp/right_conducting_required_data_manifest.json
```

Audit rows now expose:

```text
metadata_match_count
scoreable_match_count
artifact_incomplete_matches
```

The summary also includes:

```text
static_artifact_incomplete_session_count
transition_artifact_incomplete_session_count
```

## Current Workspace Result

Command:

```bash
python tools/audit_right_conducting_devset_edges.py \
  --static-root dataset/static_variants_80 \
  --transition-root dataset/transitions \
  --requirements docs/exp/right_conducting_required_data_manifest.json \
  --output-json outputs/right_conducting/devset_edge_case_audit.json \
  --output-md outputs/right_conducting/devset_edge_case_audit.md
```

Current result:

```text
static_session_count: 0
transition_session_count: 11
static_artifact_incomplete_session_count: 0
transition_artifact_incomplete_session_count: 0
p0_complete: false
P0 required/present/missing: 10 / 4 / 6
P1 required/present/missing: 4 / 4 / 0
P2 required/present/missing: 2 / 0 / 2
```

Interpretation:

```text
dataset/transitions is scoreable under the original-artifact rule.
dataset/static_variants_80 is still missing.
The next action remains fixed-camera 80 BPM static capture.
```

Readiness was regenerated after the stricter audit:

```text
outputs/right_conducting/experiment_readiness.json
outputs/right_conducting/experiment_readiness.md
```

Current readiness status:

```text
WAIT_FOR_STATIC_80_DATA
```

## Verification

Focused commands:

```bash
python -m compileall -q tools/audit_right_conducting_devset_edges.py tests/test_devset_edge_audit.py

python -m unittest discover -s tests -p 'test_devset_edge_audit.py' -v
```

Focused result:

```text
Ran 5 tests
OK
```

Full regression:

```bash
python -m unittest discover -s tests -p 'test_*.py' -v
```

Full result:

```text
Ran 137 tests in 24.047s
OK
```
