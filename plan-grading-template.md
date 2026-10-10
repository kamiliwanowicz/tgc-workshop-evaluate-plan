# QME-419 QA plan grading guide

Read `workshop/prompt.md`, the candidate `workshop/e2e-plan.md`, and relevant source files. Grade whether the plan provides useful, correct regression checks. Do not execute tests, start the application, or open a browser.

## Grading rules

Return one Markdown table with exactly 21 result rows:

| ID | Status | Evidence |
|---|---|---|
| C01 | met | Scenario 1 selects recipe A by its composition among three same-base lines; its expected edit contents distinguish it from B. |

Use each ID once, with `met` or `not_met` and one concrete reason. `met` earns the listed points; `not_met` earns zero. Keep evidence free of pipe characters so the checker can read the table.

Award points for usable setup, actions, and specific expected results. Repeating the ticket or saying "verify correct price" is insufficient. A valid check of required behavior can earn points even if the current code is defective. Invalid setup blocks only the checks that depend on it.

Accept equivalent valid data and test levels, including source-consistent fixtures with stated assumptions. API/component checks can complement browser scenarios. Timing checks need controlled response order and observations; arbitrary waits are insufficient.

Verify material compatibility, proportions, quantities/MOQ, country/currency, and prices against source. The merge must change applicable volume pricing. Numeric expectations must use independent source/fixture facts, correct component weights, rounding, and one fee per resulting blend line. Comparing displayed prices alone is insufficient.

After the table, state: `Score: <cart>/30 cart + <pricing>/30 pricing + <draft>/25 draft + <feasibility>/10 feasibility + <coverage>/5 coverage = <total>/100; gaps: <all not_met IDs or none>.` Sum only the listed weights. The checker verifies the table and arithmetic: `python tools/grading.py report.md`.

Add a short compliance note separate from the score: required path/headings, English, 1,500-word limit, and at most four scenarios. Report any verified violation of the prompt's static-only and sole-file-change rules. If process evidence is unavailable, say `unknown`; the plan alone does not prove how it was produced. Proposed future test actions are not executed actions.

## Quality rubric — 100 points

### Cart selection, edit, merge, and persistence — 30 points

| ID | Weight | What the plan must cover |
|---|---:|---|
| C01 | 5 | Edit the intended one of several different recipes sharing a base, with distinguishable cart data and an explicit check that the correct recipe opens. |
| C02 | 3 | Edit restores the selected recipe's base and ingredient materials. |
| C03 | 2 | Edit restores the selected recipe's base and ingredient ratios. |
| C04 | 2 | Edit restores the selected recipe's existing quantity. |
| C05 | 4 | A non-merging save updates that source line to the changed composition; cart observation after save confirms it persists without a duplicate. |
| C06 | 3 | A non-merging save preserves the source line's original quantity. |
| C07 | 5 | Changing a source recipe to match another existing same-base recipe yields one resulting blend line with the sum of the two original quantities; the former source recipe is absent. |
| C08 | 6 | Saving/merging leaves unrelated configured and plain cart lines unchanged, with concrete before/after composition and quantity expectations. |

### Independent, correct pricing — 30 points

| ID | Weight | What the plan must cover |
|---|---:|---|
| P01 | 5 | Identify independent source/fixture prices and a reproducible calculation method using composition, quantity, applicable component pricing, and rounding/currency rules. Reading expected values from the UI or response under test is insufficient. |
| P02 | 8 | Correct numeric material subtotal and line-total expectations for a non-merging composition edit at the preserved quantity, checked against the saved cart price. |
| P03 | 12 | A merge crosses an applicable component volume-pricing threshold; correct numeric material subtotal and line total use the combined quantity and resulting recipe, with the affected and unaffected component tiers applied correctly. |
| P04 | 5 | Explicit numeric fee expectations check that the resulting merged blend is charged one flat blending fee, rather than two fees or a fee per bag. |

### Draft preservation and late-result controls — 25 points

| ID | Weight | What the plan must cover |
|---|---:|---|
| D01 | 8 | After changing an unsaved draft, deliberately deliver a background cart-data refresh while the editor stays open; the draft retains the changed materials/ratios and source quantity. |
| D02 | 7 | Save is unavailable for a pending or unaccepted current configuration, and becomes available only after that exact current configuration is accepted; specify expected cart behavior while Save is gated. |
| D03 | 5 | Hold an earlier evaluation, change to a distinguishable current configuration, then release the earlier result after the current state/result; it cannot replace the current summary (composition and applicable price or rejection). |
| D04 | 5 | In that controlled stale-result ordering, an earlier accepted result cannot authorize a wrong save: a pending/rejected current draft leaves the cart unchanged, or a save of an accepted current draft submits only the current recipe. |

### Feasibility — 10 points

| ID | Weight | What the plan must cover |
|---|---:|---|
| F01 | 5 | Reproducible source-consistent cart/recipe fixtures and a practical setup route at a stated test level, including valid selectable materials/ratios, quantity in 25 kg bags, applicable MOQ, country/currency, and enough distinct lines for its assertions. State fixture uncertainty rather than inventing live verification. |
| F02 | 2 | Each scenario establishes its own session/cart and data; none depends on another scenario's completion. |
| F03 | 3 | Scenarios have a priority, brief risk justification, and AC references; their order reflects the regression risks. |

### Existing coverage and risks — 5 points

| ID | Weight | What the plan must cover |
|---|---:|---|
| R01 | 3 | Accurately summarize directly relevant existing E2E/lower-level coverage and explain the proposed plan's additional checks without duplicating an entire matrix. |
| R02 | 2 | Identify material requirement/source discrepancies and remaining assumptions, distinguishing required behavior, current source behavior, and unverified runtime facts. Reporting no material discrepancy is valid when supported. |

The 21 weights sum to 100. Judge each check independently. P01 can earn points for a correct independent calculation; P02/P03 also require usable saved-result checks. Do not add requirements beyond the task and rubric.
