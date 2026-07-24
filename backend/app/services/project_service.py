import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.database.models import Project
from app.schemas import ProjectCreate, ProjectUpdate


def list_projects(db: Session, user_id: uuid.UUID) -> list[Project]:
    return (
        db.query(Project)
        .filter(Project.user_id == user_id)
        .order_by(Project.created_at.desc())
        .all()
    )


def create_project(db: Session, user_id: uuid.UUID, payload: ProjectCreate) -> Project:
    project = Project(
        user_id=user_id,
        name=payload.name,
        description=payload.description,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def get_owned_project(db: Session, project_id: uuid.UUID, user_id: uuid.UUID) -> Project:
    project = (
        db.query(Project)
        .filter(Project.id == project_id, Project.user_id == user_id)
        .first()
    )

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    return project


def update_project(
    db: Session,
    project_id: uuid.UUID,
    user_id: uuid.UUID,
    payload: ProjectUpdate,
) -> Project:

    project = get_owned_project(db, project_id, user_id)

    update_data = payload.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(project, key, value)

    db.commit()
    db.refresh(project)

    return project


def delete_project(
    db: Session,
    project_id: uuid.UUID,
    user_id: uuid.UUID,
) -> None:

    project = get_owned_project(db, project_id, user_id)

    db.delete(project)
    db.commit()