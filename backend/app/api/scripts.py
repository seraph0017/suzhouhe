"""
Scripts API routes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List

from app.database import get_db
from app.models.user import User
from app.models.script import Script, ScriptStatus, ScriptVersion
from app.schemas.script import ScriptResponse, ScriptCreate, ScriptUpdate
from app.utils.security import get_current_user
from app.utils.audit_logger import log_audit_action

router = APIRouter()


@router.get("/", response_model=List[ScriptResponse])
async def list_scripts(
    project_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List scripts for a project
    """
    scripts = db.query(Script).filter(
        Script.project_id == project_id
    ).offset(skip).limit(limit).all()
    return scripts


@router.get("/{script_id}", response_model=ScriptResponse)
async def get_script(
    script_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get script by ID
    """
    script = db.query(Script).filter(Script.id == script_id).first()
    if not script:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Script not found",
        )
    return script


@router.post("/", response_model=ScriptResponse)
async def create_script(
    script_in: ScriptCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create new script
    """
    # Create initial version
    version = ScriptVersion(
        content=script_in.content,
        summary=script_in.summary,
        version=1,
        created_by=current_user.id,
    )

    script = Script(
        project_id=script_in.project_id,
        title=script_in.title,
        content=script_in.content,
        summary=script_in.summary,
        version=1,
        status=ScriptStatus.DRAFT,
    )

    db.add(script)
    db.flush()

    version.script_id = script.id
    db.add(version)
    db.commit()
    db.refresh(script)

    # Log audit action
    log_audit_action(
        db=db,
        user_id=current_user.id,
        action="CREATE",
        entity_type="SCRIPT",
        entity_id=script.id,
        project_id=script_in.project_id,
    )

    return script


@router.put("/{script_id}", response_model=ScriptResponse)
async def update_script(
    script_id: int,
    script_in: ScriptUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update script
    """
    script = db.query(Script).filter(Script.id == script_id).first()
    if not script:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Script not found",
        )

    # Check if locked
    if script.is_locked:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Script is locked and cannot be modified",
        )

    # Update fields
    update_data = script_in.model_dump(exclude_unset=True)
    new_version = False

    if "content" in update_data or "summary" in update_data:
        new_version = True
        script.version += 1

        # Create new version
        version = ScriptVersion(
            script_id=script_id,
            version=script.version,
            content=update_data.get("content", script.content),
            summary=update_data.get("summary", script.summary),
            created_by=current_user.id,
        )
        db.add(version)

    for field, value in update_data.items():
        setattr(script, field, value)

    db.add(script)
    db.commit()
    db.refresh(script)

    # Log audit action
    log_audit_action(
        db=db,
        user_id=current_user.id,
        action="UPDATE",
        entity_type="SCRIPT",
        entity_id=script.id,
        project_id=script.project_id,
        changes={"version": script.version} if new_version else {},
    )

    return script


@router.post("/{script_id}/lock", response_model=ScriptResponse)
async def lock_script(
    script_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Lock script (triggers downstream steps)
    """
    script = db.query(Script).filter(Script.id == script_id).first()
    if not script:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Script not found",
        )

    script.is_locked = True
    script.locked_at = datetime.utcnow()
    script.locked_by = current_user.id
    script.status = ScriptStatus.LOCKED

    db.add(script)
    db.commit()
    db.refresh(script)

    # Log audit action
    log_audit_action(
        db=db,
        user_id=current_user.id,
        action="LOCK",
        entity_type="SCRIPT",
        entity_id=script.id,
        project_id=script.project_id,
    )

    return script


@router.post("/{script_id}/unlock", response_model=ScriptResponse)
async def unlock_script(
    script_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Unlock script
    """
    script = db.query(Script).filter(Script.id == script_id).first()
    if not script:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Script not found",
        )

    script.is_locked = False
    script.locked_at = None
    script.locked_by = None
    script.status = ScriptStatus.DRAFT

    db.add(script)
    db.commit()
    db.refresh(script)

    return script


@router.delete("/{script_id}")
async def delete_script(
    script_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete script
    """
    script = db.query(Script).filter(Script.id == script_id).first()
    if not script:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Script not found",
        )

    db.delete(script)
    db.commit()

    # Log audit action
    log_audit_action(
        db=db,
        user_id=current_user.id,
        action="DELETE",
        entity_type="SCRIPT",
        entity_id=script.id,
        project_id=script.project_id,
    )

    return {"message": "Script deleted successfully"}
