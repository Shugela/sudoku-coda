import random
import copy
from sudoku import solve
from constants import GRID_SIZE, STARTING_MISSING, INCREMENT_PER_LEVEL

class LevelGenerator:
    @staticmethod
    def generate(level):
        # 1. Start with empty grid
        grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        
        # 2. Fill diagonal boxes for speed
        for i in range(0, GRID_SIZE, 3):
            nums = list(range(1, 10))
            random.shuffle(nums)
            for r in range(3):
                for c in range(3):
                    grid[i+r][i+c] = nums.pop()
        
        # 3. Solve to get a full valid board
        solve(grid)
        full_solution = copy.deepcopy(grid)
        
        # 4. Calculate missing cells for this level
        # Level 1 = 15, Level 2 = 18, Level 3 = 21... Level 16 = 60
        cells_to_remove = STARTING_MISSING + ((level - 1) * INCREMENT_PER_LEVEL)
        
        # Cap the difficulty so we don't remove more than 60 (leaving 21 clues)
        if cells_to_remove > 60:
            cells_to_remove = 60
            
        puzzle = copy.deepcopy(full_solution)
        indices = [(r, c) for r in range(GRID_SIZE) for c in range(GRID_SIZE)]
        random.shuffle(indices)
        
        removed = 0
        empty_cells = []
        for r, c in indices:
            if removed >= cells_to_remove: 
                break
            puzzle[r][c] = 0
            empty_cells.append((r, c))
            removed += 1
            
        # 5. Select Target Cell (must be one of the emptied ones)
        target_cell = random.choice(empty_cells)
        
        return {
            "puzzle": puzzle,
            "solution": full_solution,
            "target": target_cell
        }