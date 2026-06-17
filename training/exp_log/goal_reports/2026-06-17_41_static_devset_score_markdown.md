# Report 41 - Static Devset Score Markdown

## Scope

Report 39 introduced two devset score paths:

```text
dataset/static_variants_80
dataset/transitions
```

Both are evaluated by `tools/evaluate_motionbert_transition_margins.py`, but they have different interpretation rules.

Static 80 BPM takes do not have BPM switch events, so transition-margin filtering is inactive there. The score markdown now exposes this directly instead of presenting static devset output as a transition-margin report.

## Code Behavior

Updated:

```text
tools/evaluate_motionbert_transition_margins.py
tests/test_motionbert_transition_margin_markdown.py
```

The score payload now includes:

```text
eval_mode: static
```

when all evaluated sessions have no BPM transition times. Otherwise it remains:

```text
eval_mode: transition
```

Markdown titles:

```text
static     -> MotionBERT Static Devset Scores
transition -> MotionBERT Transition Margin Scores
```

Static interpretation focuses on:

```text
static tempo_acc
static 80 BPM recall/support
static gain_acc
P0 80 BPM recall threshold pass/fail
```

Transition interpretation still focuses on whether margin filtering recovers the `120 -> 80` stable tail.

## Why This Matters

The next required dataset is fixed-camera 80 BPM static coverage under:

```text
dataset/static_variants_80
```

That score should answer:

```text
Can the model classify stable 80 BPM when there is no transition ambiguity?
```

It should not be read as a switch-latency or transition-margin result.

## Verification

Commands:

```bash
python -m compileall -q tools/evaluate_motionbert_transition_margins.py tests/test_motionbert_transition_margin_markdown.py

python -m unittest discover -s tests -p 'test_*.py' -v
```

Result:

```text
Ran 131 tests in 24.672s
OK
```

