from constants import GRID_SIZE, SQUARE_SIZE

def is_valid(grid, r, c, v):
    for i in range(GRID_SIZE):
        if grid[r][i] == v or grid[i][c] == v:
            return False
    
    start_row, start_col = (r // SQUARE_SIZE) * SQUARE_SIZE, (c // SQUARE_SIZE) * SQUARE_SIZE
    for i in range(SQUARE_SIZE):
        for j in range(SQUARE_SIZE):
            if grid[start_row + i][start_col + j] == v:
                return False
    return True

def solve(grid):
    """Standard solver used to create the full board."""
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            if grid[r][c] == 0:
                for v in range(1, 10):
                    if is_valid(grid, r, c, v):
                        grid[r][c] = v
                        if solve(grid):
                            return True
                        grid[r][c] = 0
                return False
    return True

def count_solutions(grid):
    """
    Returns 0, 1, or 2. 
    We stop at 2 because any more doesn't matter; it's already non-unique.
    """
    count = 0
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            if grid[r][c] == 0:
                for v in range(1, 10):
                    if is_valid(grid, r, c, v):
                        grid[r][c] = v
                        count += count_solutions(grid)
                        grid[r][c] = 0
                        if count > 1: return count # Optimization
                return count
    return 1