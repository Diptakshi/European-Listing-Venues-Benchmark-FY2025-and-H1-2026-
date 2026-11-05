"""Validate the venue datapoints, then build the Excel benchmark, charts and pitch note.

    python run.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import report  # noqa: E402
import venues as vn  # noqa: E402


def main() -> None:
    d = vn.load()
    checks = vn.validate(d)
    print(checks[["check", "failures"]].to_string(index=False), "\n")
    if checks["failures"].sum():
        raise SystemExit("Data checks failed: fix the datapoints first.")
    print(vn.venue_table(d, "FY2025").to_string(index=False), "\n")
    print(vn.insights(d), "\n")
    files = [report.excel(d)] + report.charts(d)
    files.append(report.pitch_note(d, files[1:]))
    print("Written:", ", ".join(files))


if __name__ == "__main__":
    main()
