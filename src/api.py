# I use this file as the bridge between the analysis and the website.
# It gives the dashboard a way to request the same decision brief with a different seed or budget.

from functools import lru_cache
from pathlib import Path
from fastapi import FastAPI, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from .analysis import analyze

ROOT = Path(__file__).resolve().parents[2]
WEB = ROOT / "web"
app = FastAPI(title="BrandLift Lab", version="0.1.0")


@lru_cache(maxsize=32)
def _cached(seed: int, budget: int):
    # The analysis does not need to rerun when someone asks for the same view.
    return analyze(seed, float(budget))


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/brief")
def brief(seed: int = Query(17, ge=0, le=1_000_000), budget: int = Query(1_000_000, ge=100_000, le=10_000_000)):
    return _cached(seed, budget)


@app.get("/")
def index():
    return FileResponse(WEB / "index.html")


app.mount("/static", StaticFiles(directory=WEB), name="static")


def run():
    import uvicorn

    uvicorn.run("brandlift_lab.api:app", host="127.0.0.1", port=8000)
