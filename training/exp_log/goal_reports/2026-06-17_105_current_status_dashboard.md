# Report 105 - Current Status Dashboard

## Purpose

Create a short current-status entry point so the project can be understood without reading the long README, score document, or full report chain first.

## Added

```text
docs/exp/current_status.md
```

The dashboard records:

```text
overall goal: IN_PROGRESS
selected live model: TCN handmark live bundle
live runtime: GO
release validation: GO
strict independent heldout: NO_GO
remaining blocker: missing strict heldout roots
```

It also links:

```text
selected bundle paths
current supplied-set score artifacts
strict missing roots and P0 coverage
strict post-arrival script
latest verification reports
```

## Decision

Use `docs/exp/current_status.md` as the first document to open for handoff or presentation status. It does not replace the detailed score or model card; it points to the current selected model and the remaining strict heldout blocker.
