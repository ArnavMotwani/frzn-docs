# backend/app/schemas/repo.py

from datetime import datetime
from pydantic import BaseModel

class CreateRepo(BaseModel):
    owner: str
    name: str

class ReadRepo(CreateRepo):
    id: int
    full_name: str
    description: str | None = None
    default_branch: str
    html_url: str | None = None
    clone_url: str | None = None
    indexed_at: datetime

    class Config:
        orm_mode = True