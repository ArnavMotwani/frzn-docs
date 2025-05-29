from fastapi import FastAPI
from sqlmodel import SQLModel
from app.db import engine
from app.api.routers.health import router as health_router

app = FastAPI(title="frzn-docs-backend")

@app.on_event("startup")
def on_startup():
    # Auto-create tables (none defined yet, but future models will go here)
    SQLModel.metadata.create_all(engine)

# Mount the health-check router
app.include_router(health_router, prefix="")