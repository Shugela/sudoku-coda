from typing import List, Optional

from pydantic import BaseModel, Field, validator


class CellRef(BaseModel):
    row: int = Field(ge=0, le=8)
    col: int = Field(ge=0, le=8)


class SudokuHintRequest(BaseModel):
    grid: List[List[Optional[int]]]
    target: CellRef

    @validator("grid")
    def validate_grid(cls, grid):
        if len(grid) != 9:
            raise ValueError("grid must be 9x9")
        for row in grid:
            if len(row) != 9:
                raise ValueError("grid must be 9x9")
            for val in row:
                if val is None:
                    continue
                if not isinstance(val, int):
                    raise ValueError("grid values must be int or null")
                if val < 0 or val > 9:
                    raise ValueError("grid values must be between 0 and 9")
        return grid


class SudokuHintResponse(BaseModel):
    row: int = Field(ge=0, le=8)
    col: int = Field(ge=0, le=8)
    value: int = Field(ge=1, le=9)
