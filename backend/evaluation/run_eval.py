"""Run the ATS evaluation suite and write a JSON report."""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import pytest


class EvalResultCollector:
    def __init__(self):
        self.by_module = defaultdict(lambda: {"passed": 0, "failed": 0, "skipped": 0})
        self.summary = {"passed": 0, "failed": 0, "skipped": 0}

    def pytest_runtest_logreport(self, report):
        if report.when != "call" and not (
            report.when in {"setup", "teardown"} and report.failed
        ):
            if report.when == "setup" and report.skipped:
                self._record(report, "skipped")
            return

        if report.passed:
            outcome = "passed"
        elif report.failed:
            outcome = "failed"
        elif report.skipped:
            outcome = "skipped"
        else:
            return

        self._record(report, outcome)

    def _record(self, report, outcome):
        module_name = Path(report.nodeid.split("::", 1)[0]).stem
        self.by_module[module_name][outcome] += 1
        self.summary[outcome] += 1


def _format_table(by_module, summary):
    rows = [
        ("Module", "Passed", "Failed", "Skipped"),
        *[
            (
                module,
                str(counts.get("passed", 0)),
                str(counts.get("failed", 0)),
                str(counts.get("skipped", 0)),
            )
            for module, counts in sorted(by_module.items())
        ],
        (
            "TOTAL",
            str(summary["passed"]),
            str(summary["failed"]),
            str(summary["skipped"]),
        ),
    ]
    widths = [
        max(len(row[column]) for row in rows)
        for column in range(4)
    ]
    line = "+".join("-" * (width + 2) for width in widths)
    output = [f"+{line}+"]
    for index, row in enumerate(rows):
        output.append(
            "| "
            + " | ".join(
                row[column].ljust(widths[column])
                for column in range(4)
            )
            + " |"
        )
        if index == 0:
            output.append(f"+{line}+")
    output.append(f"+{line}+")
    return "\n".join(output)


def main():
    evaluation_dir = Path(__file__).resolve().parent
    result_dir = evaluation_dir / "results"
    result_dir.mkdir(parents=True, exist_ok=True)

    collector = EvalResultCollector()
    exit_code = pytest.main(
        [
            str(evaluation_dir),
            "-v",
        ],
        plugins=[collector],
    )

    total = (
        collector.summary["passed"]
        + collector.summary["failed"]
        + collector.summary["skipped"]
    )
    pass_rate = collector.summary["passed"] / total if total else 0.0
    timestamp = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    safe_timestamp = timestamp.replace(":", "-").replace("+", "Z")

    report = {
        "timestamp": timestamp,
        "summary": {
            "total": total,
            "passed": collector.summary["passed"],
            "failed": collector.summary["failed"],
            "skipped": collector.summary["skipped"],
            "pass_rate": round(pass_rate, 4),
        },
        "by_module": dict(collector.by_module),
        "pytest_exit_code": exit_code,
    }

    report_path = result_dir / f"eval_report_{safe_timestamp}.json"
    with report_path.open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2)

    print()
    print(_format_table(report["by_module"], collector.summary))
    print(f"\nPass rate: {pass_rate:.1%}")
    print(f"Report written to: {report_path}")

    return 0 if pass_rate >= 0.80 else 1


if __name__ == "__main__":
    sys.exit(main())
