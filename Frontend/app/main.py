import sys

def launch_pygame():
    print("Starting Pygame version...")
    from pygame_game import SudokuPygame
    game = SudokuPygame()
    game.run()

def launch_api():
    import uvicorn
    print("Starting Web API at http://127.0.0.1:8000")
    # Note: reload=True is great for development!
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "web":
        launch_api()
    else:
        launch_pygame()