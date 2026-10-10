# QME-419 QA plan evaluation

Evaluate the custom-blend cart-editing plan in three steps:

1. Give the grader [the guide](plan-grading-template.md), `workshop/prompt.md`, `workshop/e2e-plan.md`, and the source checkout.
2. Ask for one report with the 21 `ID | Status | Evidence` rows, score, gaps, and a short task-compliance note. Review files only; do not run the application or tests.
3. Save the report as Markdown and calculate its score:

```powershell
python tools/grading.py report.md
```

The score is out of 100: cart behavior 30, pricing 30, draft/late-result controls 25, feasibility 10, coverage/risks 5. Each check is `met` or `not_met`. The grader verifies correctness; the checker validates the report and sums points. No dependencies are required beyond Python.

Run focused checker tests with:

```powershell
python -m unittest discover -s tests -v
```

Use the same task, rubric, and source revision when comparing agent runs.
