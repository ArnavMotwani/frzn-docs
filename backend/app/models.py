# backend/app/models.py

from datetime import datetime, timezone
from typing import Optional, List, TYPE_CHECKING

from sqlmodel import SQLModel, Field, Column, Relationship
from sqlalchemy import String, ForeignKey
from pgvector.sqlalchemy import Vector
from enum import Enum

if TYPE_CHECKING:
    from .models import File, CodeChunk

class IndexStatus(str, Enum):
    pending = "pending"
    indexing = "indexing"
    complete = "complete"
    error = "error"

class Repo(SQLModel, table=True):
    __tablename__ = "repo"

    id: int = Field(None, primary_key=True)
    owner: str
    name: str
    full_name: str = Field(sa_column=Column("full_name", String, unique=True))
    description: Optional[str] = None
    default_branch: str
    html_url: Optional[str] = None
    clone_url: Optional[str] = None
    indexed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    index_status: IndexStatus = Field(default=IndexStatus.pending)

    files: List["File"] = Relationship(
        back_populates="repo",
        sa_relationship_kwargs={
            "passive_deletes": True,
            "cascade": "all, delete-orphan",
        },
    )


class File(SQLModel, table=True):
    __tablename__ = "file"

    id: int = Field(None, primary_key=True)
    repo_id: int = Field(
        sa_column=Column(ForeignKey("repo.id", ondelete="CASCADE"), nullable=True)
    )
    path: str
    size: Optional[int] = None
    indexed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    repo: "Repo" = Relationship(
        back_populates="files",
        sa_relationship_kwargs={"passive_deletes": True},
    )
    chunks: List["CodeChunk"] = Relationship(
        back_populates="file",
        sa_relationship_kwargs={
            "passive_deletes": True,
            "cascade": "all, delete-orphan",
        },
    )


class CodeChunk(SQLModel, table=True):
    __tablename__ = "codechunk"

    id: int = Field(None, primary_key=True)
    file_id: int = Field(
        sa_column=Column(ForeignKey("file.id", ondelete="CASCADE"), nullable=True)
    )
    start_line: Optional[int] = None
    end_line: Optional[int] = None
    content: str
    embedding: List[float] = Field(sa_column=Column(Vector(768)))

    file: "File" = Relationship(
        back_populates="chunks",
        sa_relationship_kwargs={"passive_deletes": True},
    )