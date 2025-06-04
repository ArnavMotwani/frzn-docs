# backend/app/models.py

from datetime import datetime
from typing import Optional, List

from sqlmodel import SQLModel, Field, Column
from sqlalchemy import String
from pgvector.sqlalchemy import Vector


class Repo(SQLModel, table=True):
    id: int = Field(None, primary_key=True)
    owner: str
    name: str
    full_name: str = Field(
        sa_column=Column("full_name", String, unique=True)
    )
    description: Optional[str] = None
    default_branch: str
    html_url: Optional[str] = None
    clone_url: Optional[str] = None
    indexed_at: datetime = Field(default_factory=datetime.utcnow)


class File(SQLModel, table=True):
    id: int = Field(None, primary_key=True)
    repo_id: int = Field(foreign_key="repo.id")
    path: str
    size: Optional[int] = None
    indexed_at: datetime = Field(default_factory=datetime.utcnow)


class CodeChunk(SQLModel, table=True):
    id: int = Field(None, primary_key=True)
    file_id: int = Field(foreign_key="file.id")
    start_line: Optional[int] = None
    end_line: Optional[int] = None
    content: str
    embedding: List[float] = Field(
        sa_column=Column(Vector(768))
    )