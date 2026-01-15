import csv
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent
LEADERBOARD_FILE = BASE_DIR / "leaderboard.csv"

def save_score(name, level, guesses, mistakes, completed):
    file_exists = LEADERBOARD_FILE.is_file()
    with LEADERBOARD_FILE.open(mode='a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["name", "datetime", "level_reached", "total_guesses", "total_mistakes", "completed"])
        writer.writerow([name, datetime.now().strftime("%Y-%m-%d %H:%M"), level, guesses, mistakes, completed])

def get_smart_leaderboard(current_player_name):
    if not LEADERBOARD_FILE.is_file():
        return {"top5": [], "player_row": None}
    
    all_scores = []
    with LEADERBOARD_FILE.open(mode='r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            all_scores.append({
                "name": row['name'],
                "level": int(row['level_reached']),
                "guesses": int(row['total_guesses']),
                "mistakes": int(row['total_mistakes']),
                "completed": row['completed']
            })
    
    # Sort: Level (desc), Guesses (asc), Mistakes (asc)
    all_scores.sort(key=lambda x: (-x['level'], x['guesses'], x['mistakes']))
    
    # Assign ranks
    for i, score in enumerate(all_scores):
        score['rank'] = i + 1

    top5 = all_scores[:5]
    player_row = None
    
    # Find the current player's best entry in the sorted list
    for score in all_scores:
        if score['name'] == current_player_name:
            player_row = score
            break # Get their highest rank entry

    return {"top5": top5, "player_row": player_row}
