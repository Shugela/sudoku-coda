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
