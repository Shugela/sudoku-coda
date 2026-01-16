import random
import copy
from sudoku import solve, count_solutions
from constants import GRID_SIZE, STARTING_MISSING, INCREMENT_PER_LEVEL

class LevelGenerator:
    @staticmethod
    def generate(level):
        # 1. Start with empty grid and fill it
        grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        
        # Fill diagonal 3x3 boxes (independent, so it's faster)
        for i in range(0, GRID_SIZE, 3):
            nums = list(range(1, 10))
            random.shuffle(nums)
            for r in range(3):
                for c in range(3):
                    grid[i+r][i+c] = nums.pop()
        
        solve(grid)
        full_solution = copy.deepcopy(grid)
        
        # 2. Determine how many cells to remove
        cells_to_remove = STARTING_MISSING + ((level - 1) * INCREMENT_PER_LEVEL)
        if cells_to_remove > 60: cells_to_remove = 60
            
        puzzle = copy.deepcopy(full_solution)
        indices = [(r, c) for r in range(GRID_SIZE) for c in range(GRID_SIZE)]
        random.shuffle(indices)
        
        removed = 0
        for r, c in indices:
            if removed >= cells_to_remove: 
                break
            
            # Temporary backup
            temp_val = puzzle[r][c]
            puzzle[r][c] = 0
            
            # Check for Unicity: If more than 1 solution exists, put it back
            if count_solutions(copy.deepcopy(puzzle)) != 1:
                puzzle[r][c] = temp_val
            else:
                removed += 1
        
        # 3. Select Target Cell (must be an empty one)
        empty_cells = [(r, c) for r in range(9) for c in range(9) if puzzle[r][c] == 0]
        target_cell = random.choice(empty_cells)
        
        # 4. Generate Advanced Hints (cells related to target)
        # These are empty cells that, if filled, help solve the target
        related_hints = []
        tr, tc = target_cell
        for r, c in empty_cells:
            if (r, c) == target_cell: continue
            # Check if in same row, col, or 3x3 box
            if r == tr or c == tc or (r//3 == tr//3 and c//3 == tc//3):
                related_hints.append((r, c))
        
        random.shuffle(related_hints)

        return {
            "puzzle": puzzle,
            "solution": full_solution,
            "target": target_cell,
            "hints_available": related_hints # Stack of specific hints
        }