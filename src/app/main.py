from fastapi import FastAPI
from app.logging import setup_logging

setup_logging()

app = FastAPI(title="Intelligent Document Parser")

@app.get("/health")
async def health() -> dict[str,str]:
    return {"status": "ok"}
