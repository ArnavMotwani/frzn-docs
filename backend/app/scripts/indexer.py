# app/scripts/indexer.py

import os
import shutil
from datetime import datetime, timezone
from git import Repo as GitPythonRepo
from sqlmodel import Session

from app.models import Repo as RepoModel, IndexStatus
from app.db import engine

def index_repo(repo: RepoModel):
    session = Session(engine)
    try:
        repo.index_status = IndexStatus.indexing
        session.add(repo)
        session.commit()
        session.refresh(repo)
    finally:
        session.close()

    clone_dir = f"/tmp/{repo.owner}_{repo.name}"
    if os.path.exists(clone_dir):
        shutil.rmtree(clone_dir)

    git_repo = GitPythonRepo.clone_from(repo.clone_url, clone_dir, depth=1)
    head_commit = git_repo.head.commit
    latest_sha = head_commit.hexsha
    print(f"Cloned (shallow) {repo.full_name} @ {latest_sha[:7]}")
    file_list = [blob.path for blob in head_commit.tree.traverse() if blob.type == "blob"]
    print("Files at HEAD:", file_list)

    session = Session(engine)
    try:
        repo.indexed_at = datetime.now(timezone.utc)
        repo.index_status = IndexStatus.complete
        session.add(repo)
        session.commit()
        session.refresh(repo)
    finally:
        session.close()

    return repo