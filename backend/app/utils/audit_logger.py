"""
Audit logging utility
"""

import json
from typing import Optional, Dict, Any
from fastapi import Request
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.models.project import Project


def log_audit_action(
    db: Session,
    user_id: int,
    action: str,
    entity_type: str,
    entity_id: Optional[int] = None,
    project_id: Optional[int] = None,
    changes: Optional[Dict[str, Any]] = None,
    request: Optional[Request] = None,
) -> AuditLog:
    """
    Log an audit action

    Args:
        db: Database session
        user_id: ID of the user performing the action
        action: Action type (e.g., 'CREATE', 'UPDATE', 'DELETE', 'LOGIN')
        entity_type: Type of entity (e.g., 'USER', 'PROJECT', 'SCRIPT')
        entity_id: ID of the affected entity
        project_id: ID of the related project
        changes: Dictionary of changes made
        request: FastAPI request object for IP and user agent

    Returns:
        Created AuditLog record
    """
    ip_address = None
    user_agent = None

    if request:
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")

    audit_log = AuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        project_id=project_id,
        changes=changes or {},
        ip_address=ip_address,
        user_agent=user_agent,
    )

    db.add(audit_log)
    db.commit()
    db.refresh(audit_log)

    return audit_log


class AuditLogger:
    """Context manager for audit logging"""

    def __init__(
        self,
        db: Session,
        user_id: int,
        action: str,
        entity_type: str,
        entity_id: Optional[int] = None,
        project_id: Optional[int] = None,
        request: Optional[Request] = None,
    ):
        self.db = db
        self.user_id = user_id
        self.action = action
        self.entity_type = entity_type
        self.entity_id = entity_id
        self.project_id = project_id
        self.request = request
        self.changes: Dict[str, Any] = {}

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            log_audit_action(
                db=self.db,
                user_id=self.user_id,
                action=self.action,
                entity_type=self.entity_type,
                entity_id=self.entity_id,
                project_id=self.project_id,
                changes=self.changes,
                request=self.request,
            )

    def add_change(self, key: str, value: Any):
        """Add a change to the log"""
        self.changes[key] = value
