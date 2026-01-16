import csv
import os
from pathlib import Path
from datetime import datetime
from collections import defaultdict

BASE_DIR = Path(__file__).resolve().parent
REPO_ROOT = BASE_DIR.parent.parent
DEFAULT_SHARED_DATA_DIR = REPO_ROOT / "Backend" / "app" / "data"
FALLBACK_DATA_DIR = BASE_DIR / "data"

ENV_DATA_DIR = os.getenv("SUDOKU_DATA_DIR")
if ENV_DATA_DIR:
    DATA_DIR = Path(ENV_DATA_DIR)
else:
    DATA_DIR = DEFAULT_SHARED_DATA_DIR if DEFAULT_SHARED_DATA_DIR.exists() else FALLBACK_DATA_DIR

STATS_FILE = DATA_DIR / "statistiques_sudoku.csv"
LEGACY_FILE = BASE_DIR / "data" / "leaderboard.csv"
HEADER = ["name", "datetime", "level", "guesses", "mistakes", "completed", "time", "streak"]


def _ensure_data_dir():
    if not DATA_DIR.exists():
        os.makedirs(DATA_DIR, exist_ok=True)


def _ensure_file(path):
    _ensure_data_dir()
    if not path.is_file():
        with path.open(mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(HEADER)
        return

    with open(path, "rb+") as f:
        f.seek(0, os.SEEK_END)
        if f.tell() > 0:
            f.seek(-1, os.SEEK_END)
            last_char = f.read(1)
            if last_char != b"\n":
                f.write(b"\n")


def _normalize_row(row):
    return {col: str(row.get(col, "")).strip() for col in HEADER}


def _row_key(row):
    normalized = _normalize_row(row)
    return tuple(normalized[col] for col in HEADER)


def _load_rows(path):
    if not path.is_file():
        return []

    rows = []
    with path.open(mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row:
                continue
            normalized = _normalize_row(row)
            if not any(normalized.values()):
                continue
            rows.append(normalized)
    return rows


def _append_rows(path, rows):
    if not rows:
        return
    _ensure_file(path)
    with path.open(mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        for row in rows:
            normalized = _normalize_row(row)
            writer.writerow([normalized[col] for col in HEADER])


def _dedupe_and_append(path, rows):
    if not rows:
        return
    existing = _load_rows(path)
    keys = set(_row_key(r) for r in existing)
    new_rows = []
    for row in rows:
        key = _row_key(row)
        if key in keys:
            continue
        keys.add(key)
        new_rows.append(row)
    _append_rows(path, new_rows)


def _merge_legacy():
    if not LEGACY_FILE.is_file():
        return
    legacy_rows = _load_rows(LEGACY_FILE)
    _dedupe_and_append(STATS_FILE, legacy_rows)

def save_score(name, level, guesses, mistakes, completed, time_taken, streak):
    _merge_legacy()
    row = {
        "name": name,
        "datetime": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "level": level,
        "guesses": guesses,
        "mistakes": mistakes,
        "completed": completed,
        "time": time_taken,
        "streak": streak,
    }
    _dedupe_and_append(STATS_FILE, [row])

def get_smart_leaderboard(current_player_name=None):
    _merge_legacy()
    if not STATS_FILE.is_file():
        return {"top5": [], "player_row": None}
    
    all_scores = []
    try:
        for row in _load_rows(STATS_FILE):
            try:
                all_scores.append({
                    "name": str(row["name"]).strip(),
                    "level": int(row["level"]),
                    "guesses": int(row["guesses"]),
                    "mistakes": int(row["mistakes"]),
                    "time": int(row["time"]),
                    "streak": int(row["streak"]),
                    "completed": str(row["completed"]).strip() == "True",
                })
            except (KeyError, ValueError):
                continue
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return {"top5": [], "player_row": None}
    
    # Sort: Level (desc), Streak (desc), Time (asc)
    all_scores.sort(key=lambda x: (-x['level'], -x['streak'], x['time']))
    
    for i, score in enumerate(all_scores):
        score['rank'] = i + 1

    return {
        "top5": all_scores[:5], 
        "player_row": next((s for s in all_scores if s['name'] == current_player_name), None)
    }


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


def get_stats():
    _merge_legacy()
    if not STATS_FILE.is_file():
        return {
            "total_games": 0,
            "completed_games": 0,
            "completion_rate": 0.0,
            "avg_level": 0.0,
            "avg_guesses": 0.0,
            "avg_mistakes": 0.0,
            "avg_time": 0.0,
            "best_level": 0,
            "best_streak": 0,
            "by_day": [],
            "recent": [],
        }

    rows = []
    for row in _load_rows(STATS_FILE):
        dt_raw = str(row.get("datetime", "")).strip()
        dt = _parse_datetime(dt_raw)
        rows.append(
            {
                "name": str(row.get("name", "")).strip(),
                "datetime": dt_raw,
                "_dt": dt,
                "level": _safe_int(row.get("level")),
                "guesses": _safe_int(row.get("guesses")),
                "mistakes": _safe_int(row.get("mistakes")),
                "time": _safe_int(row.get("time")),
                "streak": _safe_int(row.get("streak")),
                "completed": str(row.get("completed", "")).strip() == "True",
            }
        )

    if not rows:
        return {
            "total_games": 0,
            "completed_games": 0,
            "completion_rate": 0.0,
            "avg_level": 0.0,
            "avg_guesses": 0.0,
            "avg_mistakes": 0.0,
            "avg_time": 0.0,
            "best_level": 0,
            "best_streak": 0,
            "by_day": [],
            "recent": [],
        }

    total_games = len(rows)
    completed_games = sum(1 for r in rows if r["completed"])
    completion_rate = round((completed_games / total_games) * 100, 1)
    avg_level = round(sum(r["level"] for r in rows) / total_games, 2)
    avg_guesses = round(sum(r["guesses"] for r in rows) / total_games, 2)
    avg_mistakes = round(sum(r["mistakes"] for r in rows) / total_games, 2)
    avg_time = round(sum(r["time"] for r in rows) / total_games, 2)
    best_level = max(r["level"] for r in rows)
    best_streak = max(r["streak"] for r in rows)

    counts = defaultdict(int)
    for r in rows:
        if r["_dt"]:
            key = r["_dt"].strftime("%Y-%m-%d")
        elif r["datetime"]:
            key = r["datetime"].split(" ")[0]
        else:
            continue
        counts[key] += 1

    by_day = [{"date": k, "count": counts[k]} for k in sorted(counts.keys())]

    recent = sorted(
        rows,
        key=lambda r: r["_dt"] or datetime.min,
        reverse=True,
    )[:10]
    recent_payload = [
        {
            "name": r["name"],
            "datetime": r["datetime"],
            "level": r["level"],
            "time": r["time"],
            "streak": r["streak"],
            "completed": r["completed"],
        }
        for r in recent
    ]

    return {
        "total_games": total_games,
        "completed_games": completed_games,
        "completion_rate": completion_rate,
        "avg_level": avg_level,
        "avg_guesses": avg_guesses,
        "avg_mistakes": avg_mistakes,
        "avg_time": avg_time,
        "best_level": best_level,
        "best_streak": best_streak,
        "by_day": by_day,
        "recent": recent_payload,
    }
