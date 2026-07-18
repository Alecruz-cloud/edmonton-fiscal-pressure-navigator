# Product

**Adopted 2026-07-17** — practice imported from the group project (its `PRODUCT.md`),
adapted to this workspace's own identity. Nothing here overrides the Living Spec
(`CLAUDE.md`); where they could conflict, the spec wins.

## Register

Review instrument — a pre-budget brief that happens to be interactive, not a monitoring
console.

## Users

An Edmonton municipal budget or financial planning manager preparing a budget or
capital-planning review. Financially literate, verification-minded, time-poor. They open
the workspace to decide **which two or three pressure areas deserve deeper management
review** — and they will not act on a number they cannot trace.

## Product purpose

Turn eight years of Alberta municipal financial returns and CSD population estimates into
at most three transparently-tested pressure signals, each verifiable to workbook ›
schedule › variable code › year, plus a one-page management brief. Success looks like: the
manager reads the signals, opens one drill-down, checks a source trace, and walks into the
review meeting able to defend why these two or three areas — and not the other nineteen —
get the attention.

## Brand personality

Evidentiary · Measured · Traceable

An editorial, print-brief aesthetic: serif headlines, paper background, monospace
provenance stamps. It should feel like a carefully prepared review memo — the kind a
municipal CFO initials — not a control room. Calm is a feature: the tool flags pressure
without performing alarm.

## Anti-references

- **KPI-wall municipal dashboards** (default Tableau/Power BI deployments) — twenty tiles,
  no hierarchy, no verdicts. The spec bans leading with a wall of KPI cards; the
  executive view leads with at most three signals and their tests.
- **Composite fiscal-health scorecards** — a single grade invites false confidence and
  hides threshold choices. This workspace's rejected alternative; verdicts here are
  per-metric, rule-versioned, and always show their tests.
- **Real-time ops consoles** — this is an annual-cycle review instrument; freshness
  theatre (live tickers, autorefresh) would misrepresent the data's cadence.

## Design principles

1. **Signals lead; evidence is one click deep.** The first screen answers "what deserves
   review"; every claim opens to formula, trace, and data-quality notes.
2. **Every number wears its provenance.** Monospace stamps (workbook › schedule › code ›
   year) sit beside values, not in an appendix.
3. **Governance is visible in the pixels.** Chips for verified/context/provisional/draft,
   named peer sets with counts, truncation disclosed by name, not-flagged verdicts
   published — disclosures render even when inconvenient.
4. **Cautious language is part of the UI.** "Supporting context only", "can never create a
   high-priority signal", "nominal dollars", "does not make policy recommendations" appear
   where the reader's eye is, every time.
5. **Comparison without ranking theatre.** Peer displays are descriptive, coverage-labelled,
   and scale-caveated; colour encodes value, never judgment (the map ramps blue, not red).

## Accessibility & inclusion

Best effort for an internal single-user instrument: body contrast ≥ 4.5:1, no colour-only
status (every chip and dot pairs with text), keyboard-focusable tabs and controls with
visible focus, `aria` roles on the tab strip and charts, reduced-motion respected.
