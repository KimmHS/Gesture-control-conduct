# Report 99 - Strict Heldout Current Preflight

## Purpose

Re-run the strict heldout intake gates against the current worktree after the full test pass in Report 98. This confirms whether the remaining blocker is still data arrival, not code or selected TCN live bundle readiness.

## Command

```bash
python tools/run_right_conducting_goal.py \
  --steps heldout-independence,strict-heldout-scope,strict-heldout-missing-checklist,strict-heldout-preflight \
  --heldout-train-manifests outputs/right_conducting/recordings_staged_static80_transitions_manifest.json \
  --heldout-eval-roots dataset/strict_heldout_static_v1,dataset/strict_heldout_transitions_v1 \
  --heldout-independence-output-json outputs/right_conducting/selected_tcn_handmark_live45f/report99_strict_heldout_independence.json \
  --heldout-independence-output-md outputs/right_conducting/selected_tcn_handmark_live45f/report99_strict_heldout_independence.md \
  --heldout-scope-output-json outputs/right_conducting/selected_tcn_handmark_live45f/report99_strict_heldout_scope.json \
  --heldout-scope-output-md outputs/right_conducting/selected_tcn_handmark_live45f/report99_strict_heldout_scope.md \
  --heldout-target-static-root dataset/strict_heldout_static_v1 \
  --heldout-target-transition-root dataset/strict_heldout_transitions_v1 \
  --heldout-missing-output-json outputs/right_conducting/selected_tcn_handmark_live45f/report99_strict_heldout_missing_checklist.json \
  --heldout-missing-output-md outputs/right_conducting/selected_tcn_handmark_live45f/report99_strict_heldout_missing_checklist.md \
  --heldout-preflight-output-json outputs/right_conducting/selected_tcn_handmark_live45f/report99_strict_heldout_preflight.json \
  --heldout-preflight-output-md outputs/right_conducting/selected_tcn_handmark_live45f/report99_strict_heldout_preflight.md \
  --output-json outputs/right_conducting/selected_tcn_handmark_live45f/report99_strict_heldout_preflight_chain.json \
  --output-md outputs/right_conducting/selected_tcn_handmark_live45f/report99_strict_heldout_preflight_chain.md
```

## Result

```text
strict preflight: NO_GO
heldout independence: NO_GO
strict scope: NO_GO
train session count: 35
heldout session count: 0
missing heldout roots: 2
P0 required / present / missing: 8 / 0 / 8
```

Missing roots:

```text
dataset/strict_heldout_static_v1
dataset/strict_heldout_transitions_v1
```

## P0 Recording List

Record these under the strict roots, outside the staged training manifest:

| type | recording | schedule | output root |
|---|---|---|---|
| static | 80 BPM / 2 beat / large | static hold about 40s | `dataset/strict_heldout_static_v1` |
| static | 80 BPM / 2 beat / small | static hold about 40s | `dataset/strict_heldout_static_v1` |
| static | 80 BPM / 3 beat / large | static hold about 40s | `dataset/strict_heldout_static_v1` |
| static | 80 BPM / 3 beat / small | static hold about 40s | `dataset/strict_heldout_static_v1` |
| transition | 120 -> 80 -> 120 BPM / 2 beat / large | 0s:120, 15s:80, 30s:120, stop 46s | `dataset/strict_heldout_transitions_v1` |
| transition | 120 -> 80 -> 120 BPM / 2 beat / small | 0s:120, 15s:80, 30s:120, stop 46s | `dataset/strict_heldout_transitions_v1` |
| transition | 120 -> 80 -> 120 BPM / 3 beat / large | 0s:120, 15s:80, 30s:120, stop 46s | `dataset/strict_heldout_transitions_v1` |
| transition | 120 -> 80 -> 120 BPM / 3 beat / small | 0s:120, 15s:80, 30s:120, stop 46s | `dataset/strict_heldout_transitions_v1` |

Recording rules remain unchanged:

```text
fixed camera position and distance
automatic start and automatic BPM schedule only
do not press R, [, or ]
metronome audio on
no eval-local augmentation in scoring
```

## Next Command After Data Arrival

Use the Report 97 release-precheck chain first. It validates the selected TCN release before strict scoring and ends with `tcn-goal-status --fail-on-in-progress`.

```bash
python tools/run_right_conducting_goal.py \
  --dry-run \
  --steps tcn-release-validate,heldout-independence,strict-heldout-scope,strict-heldout-missing-checklist,strict-heldout-preflight,tcn-handmark-csv-stream,tcn-handmark-csv-set-score,tcn-handmark-csv-set-gate,tcn-handmark-csv-benchmark,tcn-handmark-stream-readiness,tcn-goal-status \
  --tcn-release-manifest outputs/right_conducting/selected_tcn_handmark_live45f/tcn_live_release_manifest.json \
  --tcn-release-validation-json outputs/right_conducting/selected_tcn_handmark_live45f/strict_v1_tcn_release_precheck_validation.json \
  --tcn-release-validation-md outputs/right_conducting/selected_tcn_handmark_live45f/strict_v1_tcn_release_precheck_validation.md \
  --tcn-release-validation-fail-on-no-go \
  --heldout-train-manifests outputs/right_conducting/recordings_staged_static80_transitions_manifest.json \
  --heldout-eval-roots dataset/strict_heldout_static_v1,dataset/strict_heldout_transitions_v1
```

Remove `--dry-run` only after the two strict roots exist.

## Decision

The selected TCN live path remains the current runnable model path. The full goal is still active because strict independent heldout evidence is missing. Do not report final generalization until the two strict roots are recorded and this preflight becomes `GO`.
