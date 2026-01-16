import csv
import os
from pathlib import Path
from datetime import datetime

# Path setup: current folder / data / leaderboard.csv
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
LEADERBOARD_FILE = DATA_DIR / "leaderboard.csv"

def get_smart_leaderboard(current_player_name=None):
    # Log for debugging - check your terminal to see this path!
    print(f"DEBUG: Looking for leaderboard at: {LEADERBOARD_FILE}")

    if not LEADERBOARD_FILE.is_file():
        print("DEBUG: File not found.")
        return {"top5": [], "player_row": None}
    
    all_scores = []
    try:
        with LEADERBOARD_FILE.open(mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Use .strip() on keys/values to handle accidental spaces in CSV
                all_scores.append({
                    "name": str(row.get('name', 'Unknown')).strip(),
                    "level": int(row.get('level', 0)),
                    "guesses": int(row.get('guesses', 0)),
                    "mistakes": int(row.get('mistakes', 0)),
                    "time": int(row.get('time', 0)),
                    "streak": int(row.get('streak', 0)),
                    "completed": str(row.get('completed', '')).strip() == 'True'
                })
    except Exception as e:
        print(f"DEBUG: Error reading CSV: {e}")
        return {"top5": [], "player_row": None}
    
    # Sort: Level (desc), Streak (desc), Time (asc)
    all_scores.sort(key=lambda x: (-x['level'], -x['streak'], x['time']))
    
    # Assign ranks
    for i, score in enumerate(all_scores):
        score['rank'] = i + 1

    top5 = all_scores[:5]
    player_row = next((s for s in all_scores if s['name'] == current_player_name), None)

    return {"top5": top5, "player_row": player_row}

def save_score(name, level, guesses, mistakes, completed, time_taken, streak):
    if not DATA_DIR.exists():
        os.makedirs(DATA_DIR)
        
    file_exists = LEADERBOARD_FILE.is_file()
    with LEADERBOARD_FILE.open(mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["name", "datetime", "level", "guesses", "mistakes", "completed", "time", "streak"])
        writer.writerow([name, datetime.now().strftime("%Y-%m-%d %H:%M"), level, guesses, mistakes, completed, time_taken, streak])