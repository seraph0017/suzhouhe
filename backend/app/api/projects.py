"""
Projects API routes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.user import User
from app.models.project import Project, ProjectMember, ProjectMemberRole
from app.schemas.project import ProjectResponse, ProjectCreate, ProjectUpdate
from app.utils.security import get_current_user, get_current_team_lead, get_current_admin_user
from app.utils.audit_logger import log_audit_action

router = APIRouter()


@router.get("/", response_model=List[ProjectResponse])
async def list_projects(
    skip: int = 0,
    limit: int = 100,
    status_filter: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List projects user has access to
    """
    query = db.query(Project)

    # Filter by status
    if status_filter:
        query = query.filter(Project.status == status_filter)

    # Filter by user's projects (either as lead or member)
    if current_user.role != "admin":
        member_project_ids = (
            db.query(ProjectMember.project_id)
            .filter(ProjectMember.user_id == current_user.id)
            .subquery()
        )
        query = query.filter(
            (Project.team_lead_id == current_user.id) |
            (Project.id.in_(member_project_ids))
        )

    projects = query.offset(skip).limit(limit).all()
    return projects


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get project by ID
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    # Check access
    if current_user.role != "admin":
        is_member = db.query(ProjectMember).filter(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == current_user.id
        ).first()

        if project.team_lead_id != current_user.id and not is_member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )

    return project


@router.post("/", response_model=ProjectResponse)
async def create_project(
    project_in: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_team_lead),
):
    """
    Create new project
    """
    # Use current user as team lead if not specified
    team_lead_id = project_in.team_lead_id or current_user.id

    # Create project
    project = Project(
        name=project_in.name,
        description=project_in.description,
        team_lead_id=team_lead_id,
        status="planning",
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    # Add creator as project lead if not already set
    if project.team_lead_id == current_user.id:
        member = ProjectMember(
            project_id=project.id,
            user_id=current_user.id,
            role=ProjectMemberRole.LEAD,
        )
        db.add(member)
        db.commit()

    # Log audit action
    log_audit_action(
        db=db,
        user_id=current_user.id,
        action="CREATE",
        entity_type="PROJECT",
        entity_id=project.id,
        changes={"name": project_in.name},
    )

    return project


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    project_in: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update project
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    # Check permission
    if current_user.role != "admin" and project.team_lead_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    # Update fields
    update_data = project_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)

    db.add(project)
    db.commit()
    db.refresh(project)

    # Log audit action
    log_audit_action(
        db=db,
        user_id=current_user.id,
        action="UPDATE",
        entity_type="PROJECT",
        entity_id=project.id,
        changes=update_data,
    )

    return project


@router.delete("/{project_id}")
async def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """
    Delete project (admin only)
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    db.delete(project)
    db.commit()

    # Log audit action
    log_audit_action(
        db=db,
        user_id=current_user.id,
        action="DELETE",
        entity_type="PROJECT",
        entity_id=project.id,
    )

    return {"message": "Project deleted successfully"}


@router.get("/{project_id}/members")
async def get_project_members(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get project members
    """
    members = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id
    ).all()
    return members


@router.post("/{project_id}/members")
async def add_project_member(
    project_id: int,
    user_id: int,
    role: ProjectMemberRole = ProjectMemberRole.MEMBER,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Add member to project
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    # Check permission
    if current_user.role != "admin" and project.team_lead_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    # Check if already member
    existing = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == user_id
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already a member",
        )

    member = ProjectMember(
        project_id=project_id,
        user_id=user_id,
        role=role,
    )
    db.add(member)
    db.commit()

    return member
