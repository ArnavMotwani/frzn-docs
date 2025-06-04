from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.db import get_session
from app.models import Repo
from app.schemas.repo import CreateRepo, ReadRepo

router = APIRouter(tags=["repos"])

@router.post("/repos", response_model=ReadRepo, status_code=status.HTTP_201_CREATED)
def create_repo(repo: CreateRepo, session: Session = Depends(get_session)):
    full_name = f"{repo.owner}/{repo.name}"
    existing_repo = session.exec(
        select(Repo).where(Repo.full_name == full_name)
    ).first()
    if existing_repo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Repository {full_name} already exists."
        )
    new_repo = Repo(
        owner=repo.owner,
        name=repo.name,
        full_name=full_name,
        default_branch="main",
    )
    session.add(new_repo)
    session.commit()
    session.refresh(new_repo)
    return new_repo

@router.get("/repos/{repo_id}", response_model=ReadRepo)
def read_repo(repo_id: int, session: Session = Depends(get_session)):
    repo = session.get(Repo, repo_id)
    if not repo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Repo not found"
        )
    return repo

@router.get("/repos", response_model=list[ReadRepo])
def list_repos(session: Session = Depends(get_session)):
    repos = session.exec(select(Repo)).all()
    return repos

@router.delete("/repos/{repo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_repo(repo_id: int, session: Session = Depends(get_session)):
    repo = session.get(Repo, repo_id)
    if not repo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Repo not found"
        )
    session.delete(repo)
    session.commit()
    return None