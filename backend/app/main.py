from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers.health import router as health_router
from app.api.routers.repos import router as repos_router
from app.api.routers.chat import router as chat_router

app = FastAPI(title="frzn-docs-backend")

app.include_router(health_router)
app.include_router(repos_router, prefix="/api", tags=["repos"])
app.include_router(chat_router, prefix="/api", tags=["chat"])