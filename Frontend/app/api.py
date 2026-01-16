from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
import time

from level_generator import LevelGenerator
import leaderboard

app = FastAPI()
BASE_DIR = Path(__file__).resolve().parent

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory store for the current active game session
game_state = {}

class Move(BaseModel):
    row: int
    col: int
    value: int
    is_pencil: bool = False

class FinalScore(BaseModel):
    name: str
    level: int
    guesses: int
    mistakes: int
    completed: bool
    time_taken: int
    streak: int

@app.get("/")
async def get_index():
    return FileResponse(BASE_DIR / "index.html")

@app.get("/hint_api.js")
async def get_hint_script():
    return FileResponse(BASE_DIR / "hint_api.js")

@app.get("/start")
async def start_game(level: int = 1):
    data = LevelGenerator.generate(level)
    game_id = "user_1" 
    
    game_state[game_id] = {
        "puzzle": data["puzzle"],
        "solution": data["solution"],
        "target": data["target"],
        "hints_pool": data["hints_available"], 
        "hints_used": 0,  # NEW: Initialize hint counter
        "mistakes": 0,
        "start_time": time.time()
    }
    
    return {
        "grid": data["puzzle"],
        "target": data["target"],
        "level": level,
        "server_time": time.time()
    }

@app.post("/move")
async def make_move(move: Move):
    state = game_state.get("user_1")
    if not state:
        raise HTTPException(status_code=400, detail="No game active")
    
    if move.is_pencil:
        return {"status": "pencil_recorded"}

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

@app.get("/hint")
async def get_hint():
    """Returns a hint if the player has not exceeded the 3-hint limit."""
    state = game_state.get("user_1")
    
    if not state:
        return {"error": "No game active"}

    # NEW: Check if the player already used 3 hints
    if state["hints_used"] >= 3:
        return {"error": "Hint limit reached", "remaining": 0}
    
    # Check if there are any cells available to provide a hint for
    if not state["hints_pool"]:
        return {"error": "No more cells available for hints"}
    
    # Provide the hint
    hr, hc = state["hints_pool"].pop(0)
    val = state["solution"][hr][hc]
    
    # Increment the counter
    state["hints_used"] += 1
    
    # Update the puzzle state
    state["puzzle"][hr][hc] = val
    
    return {
        "row": hr, 
        "col": hc, 
        "value": val, 
        "remaining": 3 - state["hints_used"] # Tell the frontend how many are left
    }

@app.post("/save-score")
async def save_user_score(data: FinalScore):
    leaderboard.save_score(
        data.name, data.level, data.guesses, 
        data.mistakes, data.completed, 
        data.time_taken, data.streak
    )
    return leaderboard.get_smart_leaderboard(data.name)

@app.get("/leaderboard")
async def get_leaderboard_standalone(name: str = None):
    return leaderboard.get_smart_leaderboard(name)
