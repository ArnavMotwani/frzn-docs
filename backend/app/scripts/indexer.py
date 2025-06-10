# app/scripts/indexer.py

import os
import shutil
import tempfile
from datetime import datetime, timezone
from git import Repo as GitPythonRepo
from sqlmodel import Session

from app.models import Repo as RepoModel, IndexStatus, File as FileModel
from app.db import engine
from app.utils.index_rules import should_index

def index_repo(repo_id: int):
    session = Session(engine)
    repo = session.get(RepoModel, repo_id)
    if not repo:
        return
    
    try:
        repo.index_status = IndexStatus.indexing
        session.add(repo)
        session.commit()
        session.refresh(repo)
    finally:
        session.close()

    with tempfile.TemporaryDirectory(prefix=f"{repo.owner}_{repo.name}_") as tmpdir:
        try:
            git_repo = GitPythonRepo.clone_from(repo.clone_url, tmpdir, depth=1)

            head_commit = git_repo.head.commit
            latest_sha = head_commit.hexsha
            print(f"Cloned (shallow) {repo.full_name} @ {latest_sha[:7]}")

            file_list = [blob.path for blob in head_commit.tree.traverse() if blob.type == "blob"]
            print("Files at HEAD:", file_list)

            session = Session(engine)
            try:
                for file_path in file_list:
                    if should_index(file_path):
                        file_model = FileModel(
                            repo_id=repo.id,
                            path=file_path,
                            indexed_at=datetime.now(timezone.utc)
                        )
                        session.add(file_model)
                session.commit()
            finally:
                session.close()

        except Exception as e:
            print(f"Error cloning repository {repo.full_name}: {e}")
            session = Session(engine)
            try:
                repo.index_status = IndexStatus.error
                session.add(repo)
                session.commit()
                session.refresh(repo)
            finally:
                session.close()
            return repo

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