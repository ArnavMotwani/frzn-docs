# app/scripts/indexer.py

import os
import shutil
import tempfile
from datetime import datetime, timezone
from git import Repo as GitPythonRepo
from sqlmodel import Session
from openai import OpenAI

from app.models import Repo as RepoModel, IndexStatus, File as FileModel, CodeChunk as CodeChunkModel
from app.db import engine
from app.utils.index_rules import should_index

client = OpenAI()

def create_code_chunks(file_model: FileModel, tmpdir: str, session: Session, code_chunk_size: int = 1000, batch_size: int = 100):
    file_path = os.path.join(tmpdir, file_model.path)
    if not os.path.exists(file_path):
        print(f"File {file_path} does not exist, skipping chunk creation.")
        return

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    chunks = [content[i:i + code_chunk_size] for i in range(0, len(content), code_chunk_size)]
    chunk_tuples = [(idx, chunk.strip()) for idx, chunk in enumerate(chunks) if chunk.strip()]

    for i in range(0, len(chunk_tuples), batch_size):
        batch = chunk_tuples[i:i + batch_size]
        texts = [chunk for _, chunk in batch]

        try:
            response = client.embeddings.create(
                input=texts,
                model="text-embedding-3-small"
            )
            embeddings = [item.embedding for item in response.data]
        except Exception as e:
            print(f"Embedding batch failed for file {file_model.path}: {e}")
            continue

        for (idx, chunk), embedding in zip(batch, embeddings):
            code_chunk = CodeChunkModel(
                file_id=file_model.id,
                start_line=idx * code_chunk_size + 1,
                end_line=(idx + 1) * code_chunk_size,
                content=chunk,
                embedding=embedding
            )
            session.add(code_chunk)

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
                        session.flush()
                        create_code_chunks(file_model, tmpdir, session)
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