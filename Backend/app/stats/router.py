import csv
import os
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter

router = APIRouter()

DATA_DIR = Path(
    os.getenv("SUDOKU_DATA_DIR", Path(__file__).resolve().parent.parent / "data")
)
DATA_FILE = DATA_DIR / "statistiques_sudoku.csv"


def _safe_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _parse_datetime(value):
    try:
        return datetime.strptime(value, "%Y-%m-%d %H:%M")
    except (TypeError, ValueError):
        return None


@router.get("/charts")
def get_charts():
    if not DATA_FILE.is_file():
        return {
            "connections_by_day": [],
            "avg_guesses_by_level": [],
        }

    day_counts = defaultdict(int)
    guesses_sum = defaultdict(int)
    guesses_count = defaultdict(int)

    with DATA_FILE.open(mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            dt = _parse_datetime(str(row.get("datetime", "")).strip())
            if dt:
                day_counts[dt.strftime("%Y-%m-%d")] += 1

            level = _safe_int(row.get("level"))
            guesses = _safe_int(row.get("guesses"))
            if level > 0:
                guesses_sum[level] += guesses
                guesses_count[level] += 1

    connections_by_day = [
        {"date": date, "count": day_counts[date]}
        for date in sorted(day_counts.keys())
    ]

    avg_guesses_by_level = []
    for level in sorted(guesses_sum.keys()):
        count = guesses_count.get(level, 0)
        if count:
            avg = round(guesses_sum[level] / count, 2)
            avg_guesses_by_level.append(
                {"level": level, "avg_guesses": avg}
            )

    return {
        "connections_by_day": connections_by_day,
        "avg_guesses_by_level": avg_guesses_by_level,
    }
