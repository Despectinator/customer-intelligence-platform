import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, get_current_user
from app.core.security import CurrentUser
from app.schemas import ProjectCreate, ProjectUpdate, ProjectOut
from app.services import project_service

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.get("", response_model=list[ProjectOut])
def list_projects(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    return project_service.list_projects(db, current_user.id)


@router.post("", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
def create_project(
    payload: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    return project_service.create_project(db, current_user.id, payload)


@router.get("/{project_id}", response_model=ProjectOut)
def get_project(
    project_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    return project_service.get_owned_project(db, project_id, current_user.id)


@router.put("/{project_id}", response_model=ProjectOut)
def update_project(
    project_id: uuid.UUID,
    payload: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    return project_service.update_project(db, project_id, current_user.id, payload)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    project_service.delete_project(db, project_id, current_user.id)
    return None
