import json
import os
import re
from typing import List, Optional

import requests

from app.ia.schemas import CellRef


def _extract_value(text: str) -> Optional[int]:
    try:
        payload = json.loads(text)
        if isinstance(payload, dict) and "value" in payload:
            value = int(payload["value"])
            if 1 <= value <= 9:
                return value
    except (json.JSONDecodeError, TypeError, ValueError):
        pass

    match = re.search(r"\b([1-9])\b", text)
    if match:
        return int(match.group(1))
    return None


def get_hint_for_cell(
    grid: List[List[Optional[int]]],
    row: int,
    col: int,
    target: CellRef,
) -> int:
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        raise RuntimeError("MISTRAL_API_KEY is not set")

    model = os.getenv("MISTRAL_MODEL", "open-mistral-7b")
    api_url = os.getenv(
        "MISTRAL_API_URL",
        "https://api.mistral.ai/v1/chat/completions",
    )

    system_message = (
        "You are a Sudoku solver. The grid is a 9x9 Sudoku where 0 or null means empty. "
        "Solve the puzzle using Sudoku rules, then return ONLY JSON with the value for hint_cell: "
        "{\"value\": <1-9>}. "
        "The hint_cell is NOT the target cell; never return the target cell value. "
        "Do not guess and do not include any other text."
    )
    user_payload = {
        "grid": grid,
        "target": {"row": target.row, "col": target.col},
        "hint_cell": {"row": row, "col": col},
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": json.dumps(user_payload)},
        ],
        "temperature": 0.0,
    }
    headers = {"Authorization": f"Bearer {api_key}"}

    response = requests.post(api_url, json=payload, headers=headers, timeout=30)
    response.raise_for_status()
    data = response.json()
    content = data["choices"][0]["message"]["content"]
    value = _extract_value(content)
    if value is None:
        raise RuntimeError("Mistral response did not contain a valid value")
    return value
