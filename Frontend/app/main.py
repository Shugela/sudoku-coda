import sys

def launch_pygame():
    from pygame_game import SudokuPygame
    game = SudokuPygame()
    game.run()

def launch_api():
    import uvicorn
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "web":
        launch_api()
    else:
        launch_pygame()