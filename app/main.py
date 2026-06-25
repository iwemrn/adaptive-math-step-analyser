from fastapi import FastAPI
from app.api.routers.health import router as health_router
from app.api.routers.problems import router as problems_router
from app.api.routers.attempts import router as attempts_router
from app.api.routers.profile import router as profile_router
from app.api.routers.practice import router as practice_router
from app.api.routers.admin import router as admin_router

app = FastAPI(
    title="Adaptive Math Step Analyser",
    version="0.1.0"
)

app.include_router(health_router, prefix="/health", tags=["health"])
app.include_router(problems_router, prefix="/problems", tags=["problems"])
app.include_router(attempts_router, prefix="/attempts", tags=["attempts"])
app.include_router(profile_router, prefix="/profiles", tags=["profiles"])
app.include_router(practice_router, prefix="/practice", tags=["practice"])
app.include_router(admin_router, prefix="/admin", tags=["admin"])
