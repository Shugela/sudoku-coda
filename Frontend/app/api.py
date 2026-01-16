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
    is_pencil: bool = False # New: support for pencil marks in web

class FinalScore(BaseModel):
    name: str
    level: int
    guesses: int
    mistakes: int
    completed: bool
    time_taken: int  # New
    streak: int      # New

@app.get("/")
async def get_index():
    return FileResponse(BASE_DIR / "index.html")

@app.get("/start")
async def start_game(level: int = 1):
    data = LevelGenerator.generate(level)
    game_id = "user_1" # In a real app, use a session ID
    
    game_state[game_id] = {
        "puzzle": data["puzzle"],
        "solution": data["solution"],
        "target": data["target"],
        "hints_pool": data["hints_available"], # Store hint pool
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
    
    # Logic for pencil marks doesn't need server validation for "correctness"
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
    """Returns the value of a non-target empty cell to help the player."""
    state = game_state.get("user_1")
    if not state or not state["hints_pool"]:
        return {"error": "No hints left"}
    
    # Pop the first hint from the pool we generated in level_generator
    hr, hc = state["hints_pool"].pop(0)
    val = state["solution"][hr][hc]
    
    # Update the puzzle state so the server knows this cell is now filled
    state["puzzle"][hr][hc] = val
    
    return {"row": hr, "col": hc, "value": val}

@app.post("/save-score")
async def save_user_score(data: FinalScore):
    leaderboard.save_score(
        data.name, data.level, data.guesses, 
        data.mistakes, data.completed, 
        data.time_taken, data.streak
    )
    return leaderboard.get_smart_leaderboard(data.name)