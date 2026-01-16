import csv
import os
from pathlib import Path
from datetime import datetime

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