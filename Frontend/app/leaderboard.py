import csv
import os
from pathlib import Path
from datetime import datetime

# Path setup: current folder / data / leaderboard.csv
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
LEADERBOARD_FILE = DATA_DIR / "leaderboard.csv"

def save_score(name, level, guesses, mistakes, completed, time_taken, streak):
    # Ensure the 'data' directory exists
    if not DATA_DIR.exists():
        os.makedirs(DATA_DIR)
        
    file_exists = LEADERBOARD_FILE.is_file()
    with LEADERBOARD_FILE.open(mode='a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            # Header matching the new format
            writer.writerow(["name", "datetime", "level", "guesses", "mistakes", "completed", "time", "streak"])
        writer.writerow([name, datetime.now().strftime("%Y-%m-%d %H:%M"), level, guesses, mistakes, completed, time_taken, streak])

def get_smart_leaderboard(current_player_name):
    if not LEADERBOARD_FILE.is_file():
        return {"top5": [], "player_row": None}
    
    all_scores = []
    with LEADERBOARD_FILE.open(mode='r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            all_scores.append({
                "name": row['name'],
                "level": int(row['level']),
                "guesses": int(row['guesses']),
                "mistakes": int(row['mistakes']),
                "time": int(row['time']),
                "streak": int(row['streak']),
                "completed": row['completed']
            })
    
    # Sort by Level (desc), then Streak (desc), then Time (asc)
    all_scores.sort(key=lambda x: (-x['level'], -x['streak'], x['time']))
    
    for i, score in enumerate(all_scores):
        score['rank'] = i + 1

    top5 = all_scores[:5]
    player_row = next((s for s in all_scores if s['name'] == current_player_name), None)

    return {"top5": top5, "player_row": player_row}