from fastapi import FastAPI
from app.api.routers import health, problems, attempts

app = FastAPI(
    title="Adaptive Math Step Analyser",
    version="0.1.0"
)

app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(problems.router, prefix="/problems", tags=["problems"])
app.include_router(attempts.router, prefix="/attempts", tags=["attempts"])
