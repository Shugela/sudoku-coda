from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.ia.router import router as ia_router

app = FastAPI(title="Sudoku API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ia_router, prefix="/ia", tags=["ia"])


@app.get("/health")
def health():
    return {"status": "ok"}
