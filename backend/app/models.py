# backend/app/models.py
from datetime import datetime
from sqlmodel import SQLModel, Field, Column
from sqlalchemy import String
from pgvector.sqlalchemy import Vector

class Repo(SQLModel, table=True):
    id:            int       = Field(None, primary_key=True)
    owner:         str
    name:          str
    full_name:     str       = Field(sa_column=Column("full_name", String, unique=True))
    description:   str | None = None
    default_branch:str
    html_url:      str | None = None
    clone_url:     str | None = None
    indexed_at:    datetime  = Field(default_factory=datetime.utcnow)

class File(SQLModel, table=True):
    id:            int       = Field(None, primary_key=True)
    repo_id:       int       = Field(foreign_key="repo.id")
    path:          str
    size:          int | None = None
    indexed_at:    datetime  = Field(default_factory=datetime.utcnow)

class CodeChunk(SQLModel, table=True):
    id:            int            = Field(None, primary_key=True)
    file_id:       int            = Field(foreign_key="file.id")
    start_line:    int | None     = None
    end_line:      int | None     = None
    content:       str
    embedding:     list[float]    = Field(
        sa_column=Column(Vector(768))
    )