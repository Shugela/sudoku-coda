import csv
import os
from pathlib import Path
from datetime import datetime
from collections import defaultdict

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
LEADERBOARD_FILE = DATA_DIR / "leaderboard.csv"

def save_score(name, level, guesses, mistakes, completed, time_taken, streak):
    if not DATA_DIR.exists():
        os.makedirs(DATA_DIR)
        
    file_exists = LEADERBOARD_FILE.is_file()
    
    # Check if we need to add a missing newline to the end of the file first
    if file_exists:
        with open(LEADERBOARD_FILE, 'rb+') as f:
            f.seek(0, os.SEEK_END)
            if f.tell() > 0:
                f.seek(-1, os.SEEK_END)
                last_char = f.read(1)
                if last_char != b'\n':
                    f.write(b'\n')

    # Now append the new row safely
    with LEADERBOARD_FILE.open(mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["name", "datetime", "level", "guesses", "mistakes", "completed", "time", "streak"])
        
        writer.writerow([name, datetime.now().strftime("%Y-%m-%d %H:%M"), level, guesses, mistakes, completed, time_taken, streak])

def get_smart_leaderboard(current_player_name=None):
    if not LEADERBOARD_FILE.is_file():
        return {"top5": [], "player_row": None}
    
    all_scores = []
    try:
        with LEADERBOARD_FILE.open(mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    all_scores.append({
                        "name": str(row['name']).strip(),
                        "level": int(row['level']),
                        "guesses": int(row['guesses']),
                        "mistakes": int(row['mistakes']),
                        "time": int(row['time']),
                        "streak": int(row['streak']),
                        "completed": str(row['completed']).strip() == 'True'
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
    if not LEADERBOARD_FILE.is_file():
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
    with LEADERBOARD_FILE.open(mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
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
