from constants import GRID_SIZE, SQUARE_SIZE

def is_valid(grid, r, c, v):
    # Check row and column
    for i in range(GRID_SIZE):
        if grid[r][i] == v or grid[i][c] == v:
            return False
    
    # Check 3x3 box
    start_row, start_col = (r // SQUARE_SIZE) * SQUARE_SIZE, (c // SQUARE_SIZE) * SQUARE_SIZE
    for i in range(SQUARE_SIZE):
        for j in range(SQUARE_SIZE):
            if grid[start_row + i][start_col + j] == v:
                return False
    return True

def solve(grid):
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