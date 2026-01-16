import requests
from fastapi import APIRouter, HTTPException

from app.ia.mistral_client import get_hint_for_cell
from app.ia.schemas import SudokuHintRequest, SudokuHintResponse
from app.ia.solver import select_random_empty_peer_cell

router = APIRouter()


@router.post("/hint", response_model=SudokuHintResponse)
def hint(request: SudokuHintRequest) -> SudokuHintResponse:
    cell = select_random_empty_peer_cell(request.grid, request.target)
    if cell is None:
        raise HTTPException(
            status_code=400,
            detail="no empty cell in target row or column",
        )

    row, col = cell
    try:
        value = get_hint_for_cell(request.grid, row, col, request.target)
    except requests.RequestException as exc:
        raise HTTPException(status_code=502, detail="mistral api error") from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return SudokuHintResponse(row=row, col=col, value=value)
