import io
import re
import sys
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import grading


def report(rows=None):
    if rows is None:
        rows = [(identifier, "met", f"Evidence for {identifier}.") for identifier in grading.WEIGHTS]
    body = "\n".join(f"| {identifier} | {status} | {evidence} |" for identifier, status, evidence in rows)
    return f"| ID | Status | Evidence |\n|---|---|---|\n{body}\n"


class GradingTests(unittest.TestCase):
    def test_weights_total_100_and_guide_matches_checker(self):
        self.assertEqual({name: sum(group.values()) for name, group in grading.GROUP_WEIGHTS.items()},
                         {"cart": 30, "pricing": 30, "draft": 25, "feasibility": 10, "coverage": 5})
        self.assertEqual(len(grading.WEIGHTS), 21)
        self.assertEqual(sum(grading.WEIGHTS.values()), 100)
        guide = (Path(__file__).resolve().parents[1] / "plan-grading-template.md").read_text(encoding="utf-8")
        listed = {identifier: int(weight) for identifier, weight in re.findall(r"\|\s*([CPDFR]\d{2})\s*\|\s*(\d+)\s*\|", guide)}
        self.assertEqual(listed, grading.WEIGHTS)

    def test_correct_report_sum_and_gaps(self):
        self.assertEqual(grading.score_report(report()),
                         {"cart": 30, "pricing": 30, "draft": 25, "feasibility": 10,
                          "coverage": 5, "total": 100, "gaps": []})
        self.assertEqual(grading.score_report(report() + "\nDeclared score: 0/100; gaps: C01\n")["total"], 100)
        rows = [(identifier, "not_met" if identifier in {"C01", "P03", "D01", "F02", "R02"} else "met",
                 f"Evidence for {identifier}.") for identifier in reversed(grading.WEIGHTS)]
        score = grading.score_report(report(rows))
        self.assertEqual(score, {"cart": 25, "pricing": 18, "draft": 17, "feasibility": 8,
                                 "coverage": 3, "total": 71, "gaps": ["C01", "D01", "F02", "P03", "R02"]})

    def test_all_not_met_scores_zero(self):
        rows = [(identifier, "not_met", "Missing.") for identifier in grading.WEIGHTS]
        score = grading.score_report(report(rows))
        self.assertEqual(score["total"], 0)
        self.assertEqual(score["gaps"], sorted(grading.WEIGHTS))

    def test_missing_duplicate_and_unknown_ids_rejected(self):
        rows = list((identifier, "met", "Evidence.") for identifier in grading.WEIGHTS)
        with self.assertRaisesRegex(ValueError, "exactly 21"):
            grading.score_report(report(rows[:-1]))
        with self.assertRaisesRegex(ValueError, "exactly 21"):
            grading.score_report(report(rows + [("C99", "met", "Extra.")]))
        duplicate = rows.copy()
        duplicate[1] = (duplicate[0][0], "met", "Evidence.")
        with self.assertRaisesRegex(ValueError, "duplicate ID"):
            grading.score_report(report(duplicate))
        unknown = rows.copy()
        unknown[0] = ("C99", "met", "Evidence.")
        with self.assertRaisesRegex(ValueError, "unknown ID"):
            grading.score_report(report(unknown))

    def test_invalid_status_and_empty_evidence_rejected(self):
        rows = [(identifier, "met", "Evidence.") for identifier in grading.WEIGHTS]
        rows[0] = (rows[0][0], "blocked", "Evidence.")
        with self.assertRaisesRegex(ValueError, "status must be"):
            grading.score_report(report(rows))
        rows[0] = (rows[0][0], "met", "  ")
        with self.assertRaisesRegex(ValueError, "evidence is empty"):
            grading.score_report(report(rows))

    def test_table_headers_columns_and_row_boundaries(self):
        with self.assertRaisesRegex(ValueError, "expected one table"):
            grading.score_report("No table.\n")
        with self.assertRaisesRegex(ValueError, "expected one table"):
            grading.score_report(report() + report())
        with self.assertRaisesRegex(ValueError, "expected three columns"):
            grading.score_report(report().replace("Evidence for C01.", "Evidence | extra"))
        with self.assertRaisesRegex(ValueError, "malformed Markdown table row"):
            grading.score_report(report().replace("| C01 | met | Evidence for C01. |",
                                                 "| C01 | met | Evidence for C01."))
        with self.assertRaisesRegex(ValueError, "exactly 21"):
            grading.score_report(report().replace("| C02 |", "\n| C02 |"))
        without_separator = report().replace("|---|---|---|\n", "")
        self.assertEqual(grading.score_report(without_separator)["total"], 100)

    def test_cli_prints_computed_score_and_rejects_invalid_report(self):
        output = io.StringIO()
        with patch.object(sys, "argv", ["grading.py", "report.md"]), \
                patch.object(Path, "read_text", return_value=report()), redirect_stdout(output):
            grading.main()
        self.assertEqual(output.getvalue(),
                         "Score: 30/30 cart + 30/30 pricing + 25/25 draft + 10/10 feasibility + 5/5 coverage = 100/100\nGaps: none\n")
        error = io.StringIO()
        with patch.object(sys, "argv", ["grading.py", "report.md"]), \
                patch.object(Path, "read_text", return_value="Invalid"), redirect_stderr(error):
            with self.assertRaises(SystemExit) as raised:
                grading.main()
        self.assertEqual(raised.exception.code, 2)
        self.assertIn("Invalid grading report:", error.getvalue())


if __name__ == "__main__":
    unittest.main()
