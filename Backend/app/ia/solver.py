import random
from typing import List, Optional, Tuple

from app.ia.schemas import CellRef


def is_empty(value: Optional[int]) -> bool:
    return value is None or value == 0


def select_random_empty_peer_cell(
    grid: List[List[Optional[int]]],
    target: CellRef,
) -> Optional[Tuple[int, int]]:
    row = target.row
    col = target.col
    candidates = []
    for c in range(9):
        if c == col:
            continue
        if is_empty(grid[row][c]):
            candidates.append((row, c))
    for r in range(9):
        if r == row:
            continue
        if is_empty(grid[r][col]):
            candidates.append((r, col))
    if not candidates:
        return None
    return random.choice(candidates)


def _normalize_grid(grid: List[List[Optional[int]]]) -> List[List[int]]:
    return [[0 if v is None else int(v) for v in row] for row in grid]


def _is_valid_start(grid: List[List[int]]) -> bool:
    for r in range(9):
        seen = set()
        for c in range(9):
            val = grid[r][c]
            if val == 0:
                continue
            if val in seen:
                return False
            seen.add(val)

    for c in range(9):
        seen = set()
        for r in range(9):
            val = grid[r][c]
            if val == 0:
                continue
            if val in seen:
                return False
            seen.add(val)

    for box_r in range(0, 9, 3):
        for box_c in range(0, 9, 3):
            seen = set()
            for r in range(box_r, box_r + 3):
                for c in range(box_c, box_c + 3):
                    val = grid[r][c]
                    if val == 0:
                        continue
                    if val in seen:
                        return False
                    seen.add(val)

    return True


def _can_place(grid: List[List[int]], row: int, col: int, value: int) -> bool:
    if any(grid[row][c] == value for c in range(9)):
        return False
    if any(grid[r][col] == value for r in range(9)):
        return False

    box_r = (row // 3) * 3
    box_c = (col // 3) * 3
    for r in range(box_r, box_r + 3):
        for c in range(box_c, box_c + 3):
            if grid[r][c] == value:
                return False
    return True


def _solve_grid(grid: List[List[int]]) -> bool:
    for r in range(9):
        for c in range(9):
            if grid[r][c] == 0:
                for value in range(1, 10):
                    if _can_place(grid, r, c, value):
                        grid[r][c] = value
                        if _solve_grid(grid):
                            return True
                        grid[r][c] = 0
                return False
    return True


def solve_sudoku(grid: List[List[Optional[int]]]) -> Optional[List[List[int]]]:
    normalized = _normalize_grid(grid)
    if not _is_valid_start(normalized):
        return None

    working = [row[:] for row in normalized]
    if not _solve_grid(working):
        return None
    return working


def get_solution_value(
    grid: List[List[Optional[int]]],
    row: int,
    col: int,
) -> int:
    solved = solve_sudoku(grid)
    if solved is None:
        raise ValueError("unsolvable grid")
    return solved[row][col]
