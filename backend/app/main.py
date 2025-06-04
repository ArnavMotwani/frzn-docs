from fastapi import FastAPI
from app.api.routers.health import router as health_router
from app.api.routers.repos import router as repos_router

app = FastAPI(title="frzn-docs-backend")

app.include_router(health_router)
app.include_router(repos_router, prefix="/api", tags=["repos"])