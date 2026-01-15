from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from level_generator import LevelGenerator
import leaderboard

app = FastAPI()
BASE_DIR = Path(__file__).resolve().parent

# 1. MIDDLEWARE FIRST
# This ensures CORS is active for all routes below
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    # Ensure index.html is in the same folder as api.py
    return {"status": "healthy"}

# 2. ROUTES
@app.get("/")
async def get_index():
    # Ensure index.html is in the same folder as api.py
    return FileResponse(BASE_DIR / "index.html")

# In-memory store for the current active game session
game_state = {}

class Move(BaseModel):
    row: int
    col: int
    value: int

class FinalScore(BaseModel):
    name: str
    level: int
    guesses: int
    mistakes: int
    completed: bool

@app.get("/start")
async def start_game(level: int = 1):
    data = LevelGenerator.generate(level)
    game_id = "user_1" 
    
    game_state[game_id] = {
        "puzzle": data["puzzle"],
        "solution": data["solution"],
        "target": data["target"],
        "mistakes": 0
    }
    
    return {
        "grid": data["puzzle"],
        "target": data["target"],
        "level": level
    }

@app.post("/move")
async def make_move(move: Move):
    state = game_state.get("user_1")
    if not state:
        raise HTTPException(status_code=400, detail="No game active")
    
    correct_val = state["solution"][move.row][move.col]
    is_correct = (move.value == correct_val)
    is_target = [move.row, move.col] == list(state["target"])
    
    if not is_correct:
        state["mistakes"] += 1
    
    return {
        "correct": is_correct,
        "mistakes": state["mistakes"],
        "success": is_correct and is_target,
        "failed": state["mistakes"] >= 3
    }

@app.get("/leaderboard")
async def get_leaderboard(name: str):
    return leaderboard.get_smart_leaderboard(name)

@app.post("/save-score")
async def save_user_score(data: FinalScore):
    leaderboard.save_score(data.name, data.level, data.guesses, data.mistakes, data.completed)
    return leaderboard.get_smart_leaderboard(data.name)
