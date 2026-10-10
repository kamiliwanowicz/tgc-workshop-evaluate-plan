"""Score a Markdown grading report; standard library only."""
import argparse
import re
from pathlib import Path

GROUP_WEIGHTS = {
    "cart": {"C01": 5, "C02": 3, "C03": 2, "C04": 2,
             "C05": 4, "C06": 3, "C07": 5, "C08": 6},
    "pricing": {"P01": 5, "P02": 8, "P03": 12, "P04": 5},
    "draft": {"D01": 8, "D02": 7, "D03": 5, "D04": 5},
    "feasibility": {"F01": 5, "F02": 2, "F03": 3},
    "coverage": {"R01": 3, "R02": 2},
}
WEIGHTS = {identifier: weight for group in GROUP_WEIGHTS.values()
           for identifier, weight in group.items()}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def cells(line, number):
    line = line.strip()
    require(line.startswith("|") and line.endswith("|"), f"line {number}: malformed Markdown table row")
    return [cell.strip() for cell in line[1:-1].split("|")]


def score_report(text):
    lines = text.splitlines()
    headers = [i for i, line in enumerate(lines) if line.strip().startswith("|")
               and line.strip().endswith("|") and cells(line, i + 1) == ["ID", "Status", "Evidence"]]
    require(len(headers) == 1, "expected one table headed | ID | Status | Evidence |")
    rows, index = [], headers[0] + 1
    if index < len(lines) and lines[index].strip().startswith("|"):
        separator = cells(lines[index], index + 1)
        if len(separator) == 3 and all(re.fullmatch(r":?-{3,}:?", x) for x in separator):
            index += 1
    while index < len(lines) and lines[index].strip().startswith("|"):
        row = cells(lines[index], index + 1)
        require(len(row) == 3, f"line {index + 1}: expected three columns")
        rows.append(row)
        index += 1
    require(len(rows) == len(WEIGHTS), f"expected exactly {len(WEIGHTS)} result rows, found {len(rows)}")
    seen, earned = set(), set()
    for offset, (identifier, status, evidence) in enumerate(rows, headers[0] + 2):
        require(identifier in WEIGHTS, f"row {offset}: unknown ID {identifier!r}")
        require(identifier not in seen, f"row {offset}: duplicate ID {identifier}")
        require(status in {"met", "not_met"}, f"row {offset} ({identifier}): status must be met or not_met")
        require(bool(evidence.strip()), f"row {offset} ({identifier}): evidence is empty")
        seen.add(identifier)
        if status == "met":
            earned.add(identifier)
    require(seen == set(WEIGHTS), "result rows do not contain the complete known ID set")
    scores = {name: sum(weight for identifier, weight in group.items() if identifier in earned)
              for name, group in GROUP_WEIGHTS.items()}
    return {**scores, "total": sum(scores.values()), "gaps": sorted(set(WEIGHTS) - earned)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", help="Markdown report with the 21-row ID/Status/Evidence table")
    args = parser.parse_args()
    try:
        score = score_report(Path(args.report).read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        parser.exit(2, f"Invalid grading report: {error}\n")
    breakdown = " + ".join(f"{score[name]}/{sum(group.values())} {name}"
                           for name, group in GROUP_WEIGHTS.items())
    print(f"Score: {breakdown} = {score['total']}/100")
    print("Gaps: " + (", ".join(score["gaps"]) or "none"))


if __name__ == "__main__":
    main()
