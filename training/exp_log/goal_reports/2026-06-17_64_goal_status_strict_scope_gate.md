# Goal Status Strict Scope Gate

## Summary

The selected ext MotionBERT 45f bundle now reports strict heldout scope as a first-class goal status gate.

```text
bundle: outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext
goal_status: outputs/right_conducting/goal_status_selected_motionbert_live45f_ext.json
goal_status_md: outputs/right_conducting/goal_status_selected_motionbert_live45f_ext.md
live_pilot_status: GO
strict_heldout_status: NO_GO
final_status: IN_PROGRESS
```

## Current Gate Result

| gate | status | note |
|---|---|---|
| deployment live replay | GO | fixed-camera deployment-fit replay passes |
| realtime benchmark | PASS | p90 11.6339 ms, headroom 17.1911 |
| label-free/online pose stream | PASS | pose-only live output rows exist for static80 and transition samples |
| heldout independence | GO | current eval roots do not overlap the staged train manifest |
| strict heldout scope | NO_GO | P0 in-scope coverage is 0 / 8 |
| strict live replay | NO_GO | available 222455 stress session fails and is outside current 2/3-beat target scope |

## Interpretation

The selected model is usable as the current fixed-camera live pilot candidate, but it is not ready to be presented as strict heldout/generalization evidence.

The blocking issue is no longer only score quality. The available independent eval roots are not the right heldout scope for the current target:

```text
needed P0 heldout:
- static 80 BPM, beat 2/3, large/small
- 120 -> 80 -> 120, beat 2/3, large/small
```

## Verification

```bash
python -m py_compile lib/right_conducting/goal_status.py tools/summarize_right_conducting_goal_status.py
python -m unittest discover -s tests -p 'test_goal_status.py' -v
python tools/summarize_right_conducting_goal_status.py \
  --manifest outputs/right_conducting/selected_motionbert_static80_transitions_live45f_ext/motionbert_conducting_live_manifest.json \
  --output-json outputs/right_conducting/goal_status_selected_motionbert_live45f_ext.json \
  --output-md outputs/right_conducting/goal_status_selected_motionbert_live45f_ext.md
```

All checks above passed.

