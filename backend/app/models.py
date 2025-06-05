# backend/app/models.py

from datetime import datetime, timezone
from typing import Optional, List

from sqlmodel import SQLModel, Field, Column
from sqlalchemy import String
from pgvector.sqlalchemy import Vector
from enum import Enum

class IndexStatus(str, Enum):
    pending = "pending"
    indexing = "indexing"
    complete = "complete"
    error = "error"


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
    indexed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    index_status: IndexStatus = Field(default=IndexStatus.pending)


class File(SQLModel, table=True):
    id: int = Field(None, primary_key=True)
    repo_id: int = Field(foreign_key="repo.id")
    path: str
    size: Optional[int] = None
    indexed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CodeChunk(SQLModel, table=True):
    id: int = Field(None, primary_key=True)
    file_id: int = Field(foreign_key="file.id")
    start_line: Optional[int] = None
    end_line: Optional[int] = None
    content: str
    embedding: List[float] = Field(
        sa_column=Column(Vector(768))
    )