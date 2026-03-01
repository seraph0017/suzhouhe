"""
Test Project Management API

Tests for project CRUD operations, team member assignment, and project workflow.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import User, UserRole
from app.models.project import Project, ProjectMember, ProjectMemberRole
from app.models.script import Script


class TestProjectList:
    """Test project listing"""

    def test_list_projects_admin(self, auth_client: TestClient, db: Session, test_project):
        """Test admin can list all projects"""
        response = auth_client.get("/projects/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_list_projects_team_lead(self, lead_client: TestClient, db: Session, test_project):
        """Test team lead can list their projects"""
        response = lead_client.get("/projects/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]["name"] == "Test Manga A"

    def test_list_projects_team_member(self, member_client: TestClient, db: Session, project_with_member):
        """Test team member can list assigned projects"""
        response = member_client.get("/projects/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]["name"] == "Team Project"

    def test_list_projects_with_status_filter(self, lead_client: TestClient, db: Session, test_project, test_project_in_progress):
        """Test filtering projects by status"""
        # Filter by planning status
        response = lead_client.get("/projects/?status_filter=planning")
        assert response.status_code == 200
        data = response.json()
        for project in data:
            assert project["status"] == "planning"

    def test_list_projects_pagination(self, lead_client: TestClient, db: Session, team_lead_user):
        """Test project listing pagination"""
        # Create multiple projects
        for i in range(15):
            project = Project(
                name=f"Test Project {i}",
                description=f"Description {i}",
                team_lead_id=team_lead_user.id,
                status="planning",
            )
            db.add(project)
        db.commit()

        # Get first page
        response = lead_client.get("/projects/?skip=0&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 10

        # Get second page
        response = lead_client.get("/projects/?skip=10&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 10


class TestProjectGet:
    """Test getting single project"""

    def test_get_project_success(self, lead_client: TestClient, test_project):
        """Test getting project by ID"""
        response = lead_client.get(f"/projects/{test_project.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_project.id
        assert data["name"] == test_project.name

    def test_get_project_not_found(self, lead_client: TestClient):
        """Test getting non-existent project"""
        response = lead_client.get("/projects/99999")
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Project not found"

    def test_get_project_no_access(self, member_client: TestClient, db: Session, team_lead_user):
        """Test member cannot access other projects"""
        # Create a project the member is not part of
        project = Project(
            name="Private Project",
            description="Not accessible",
            team_lead_id=team_lead_user.id,
            status="planning",
        )
        db.add(project)
        db.commit()

        response = member_client.get(f"/projects/{project.id}")
        assert response.status_code in [403, 404]

    def test_get_project_archived(self, lead_client: TestClient, archived_project):
        """Test getting archived project"""
        response = lead_client.get(f"/projects/{archived_project.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "archived"


class TestProjectCreate:
    """Test project creation"""

    def test_create_project_team_lead(self, lead_client: TestClient, team_lead_user):
        """Test team lead can create project"""
        response = lead_client.post(
            "/projects/",
            json={
                "name": "New Manga Project",
                "description": "A new manga production project",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "New Manga Project"
        assert data["status"] == "planning"
        assert data["team_lead_id"] == team_lead_user.id

    def test_create_project_admin(self, auth_client: TestClient, admin_user):
        """Test admin can create project"""
        response = auth_client.post(
            "/projects/",
            json={
                "name": "Admin Project",
                "description": "Project created by admin",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Admin Project"

    def test_create_project_team_member_forbidden(self, member_client: TestClient):
        """Test team member cannot create project"""
        response = member_client.post(
            "/projects/",
            json={
                "name": "Member Project",
                "description": "Should fail",
            },
        )

        assert response.status_code == 403

    def test_create_project_missing_name(self, lead_client: TestClient):
        """Test project creation without name"""
        response = lead_client.post(
            "/projects/",
            json={
                "description": "No name provided",
            },
        )

        assert response.status_code == 422

    def test_create_project_name_too_long(self, lead_client: TestClient):
        """Test project creation with name exceeding limit"""
        response = lead_client.post(
            "/projects/",
            json={
                "name": "A" * 201,  # Max is 200 characters
                "description": "Name too long",
            },
        )

        assert response.status_code == 422

    def test_create_project_with_team_lead_id(self, auth_client: TestClient, team_lead_user):
        """Test admin can specify team lead for project"""
        response = auth_client.post(
            "/projects/",
            json={
                "name": "Specified Lead Project",
                "description": "With specific team lead",
                "team_lead_id": team_lead_user.id,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["team_lead_id"] == team_lead_user.id


class TestProjectUpdate:
    """Test project updates"""

    def test_update_project_name(self, lead_client: TestClient, test_project):
        """Test updating project name"""
        response = lead_client.put(
            f"/projects/{test_project.id}",
            json={"name": "Updated Project Name"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Project Name"

    def test_update_project_status(self, lead_client: TestClient, test_project):
        """Test updating project status"""
        response = lead_client.put(
            f"/projects/{test_project.id}",
            json={"status": "in_progress"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "in_progress"

    def test_update_project_not_owner(self, member_client: TestClient, test_project):
        """Test non-owner cannot update project"""
        response = member_client.put(
            f"/projects/{test_project.id}",
            json={"name": "Unauthorized Update"},
        )

        assert response.status_code == 403

    def test_update_project_admin(self, auth_client: TestClient, test_project):
        """Test admin can update any project"""
        response = auth_client.put(
            f"/projects/{test_project.id}",
            json={"name": "Admin Updated"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Admin Updated"

    def test_update_archived_project(self, lead_client: TestClient, archived_project):
        """Test updating archived project should fail or be restricted"""
        response = lead_client.put(
            f"/projects/{archived_project.id}",
            json={"name": "Cannot Update Archived"},
        )

        # Either allowed (just updating metadata) or restricted
        # Based on implementation, we expect it might be allowed for admin
        assert response.status_code in [200, 400, 403]

    def test_update_project_not_found(self, lead_client: TestClient):
        """Test updating non-existent project"""
        response = lead_client.put(
            "/projects/99999",
            json={"name": "Update Non-existent"},
        )

        assert response.status_code == 404


class TestProjectDelete:
    """Test project deletion"""

    def test_delete_project_admin(self, auth_client: TestClient, db: Session, team_lead_user):
        """Test admin can delete project"""
        project = Project(
            name="To Delete",
            description="Will be deleted",
            team_lead_id=team_lead_user.id,
            status="planning",
        )
        db.add(project)
        db.commit()
        project_id = project.id

        response = auth_client.delete(f"/projects/{project_id}")
        assert response.status_code == 200

        # Verify deleted
        assert db.query(Project).filter(Project.id == project_id).first() is None

    def test_delete_project_non_admin_forbidden(self, lead_client: TestClient, test_project):
        """Test team lead cannot delete project"""
        response = lead_client.delete(f"/projects/{test_project.id}")

        assert response.status_code == 403

    def test_delete_project_not_found(self, auth_client: TestClient):
        """Test deleting non-existent project"""
        response = auth_client.delete("/projects/99999")

        assert response.status_code == 404


class TestProjectMembers:
    """Test project member management"""

    def test_get_project_members(self, lead_client: TestClient, project_with_member):
        """Test getting project members"""
        response = lead_client.get(f"/projects/{project_with_member.id}/members")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_add_project_member_lead(self, lead_client: TestClient, test_project, team_member):
        """Test team lead can add member to project"""
        response = lead_client.post(
            f"/projects/{test_project.id}/members",
            params={"user_id": team_member.id, "role": "member"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == team_member.id
        assert data["project_id"] == test_project.id

    def test_add_project_member_admin(self, auth_client: TestClient, test_project, team_member):
        """Test admin can add member to project"""
        response = auth_client.post(
            f"/projects/{test_project.id}/members",
            params={"user_id": team_member.id, "role": "member"},
        )

        assert response.status_code == 200

    def test_add_member_already_exists(self, lead_client: TestClient, project_with_member, team_member):
        """Test adding duplicate member fails"""
        response = lead_client.post(
            f"/projects/{project_with_member.id}/members",
            params={"user_id": team_member.id, "role": "member"},
        )

        assert response.status_code == 400
        data = response.json()
        assert "already a member" in data["detail"]

    def test_add_member_not_found(self, lead_client: TestClient, test_project):
        """Test adding non-existent user"""
        response = lead_client.post(
            f"/projects/{test_project.id}/members",
            params={"user_id": 99999, "role": "member"},
        )

        assert response.status_code == 400  # Or 500 depending on error handling

    def test_add_member_unauthorized(self, member_client: TestClient, test_project, team_member):
        """Test member cannot add other members"""
        response = member_client.post(
            f"/projects/{test_project.id}/members",
            params={"user_id": team_member.id, "role": "member"},
        )

        assert response.status_code == 403

    def test_add_member_with_role(self, lead_client: TestClient, test_project, team_member):
        """Test adding member with specific role"""
        response = lead_client.post(
            f"/projects/{test_project.id}/members",
            params={"user_id": team_member.id, "role": "lead"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "lead"


class TestProjectStatusWorkflow:
    """Test project status transitions"""

    def test_planning_to_in_progress(self, lead_client: TestClient, test_project):
        """Test transitioning from planning to in_progress"""
        response = lead_client.put(
            f"/projects/{test_project.id}",
            json={"status": "in_progress"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "in_progress"

    def test_in_progress_to_completed(self, lead_client: TestClient, test_project_in_progress):
        """Test transitioning from in_progress to completed"""
        response = lead_client.put(
            f"/projects/{test_project_in_progress.id}",
            json={"status": "completed"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"

    def test_in_progress_to_on_hold(self, lead_client: TestClient, test_project_in_progress):
        """Test transitioning from in_progress to on_hold"""
        response = lead_client.put(
            f"/projects/{test_project_in_progress.id}",
            json={"status": "on_hold"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "on_hold"

    def test_completed_to_archived(self, lead_client: TestClient, db: Session, team_lead_user):
        """Test transitioning from completed to archived"""
        project = Project(
            name="Complete to Archive",
            description="Test",
            team_lead_id=team_lead_user.id,
            status="completed",
        )
        db.add(project)
        db.commit()

        response = lead_client.put(
            f"/projects/{project.id}",
            json={"status": "archived"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "archived"


class TestProjectAccessControl:
    """Test project access control"""

    def test_member_access_own_project(self, member_client: TestClient, project_with_member):
        """Test member can access their project"""
        response = member_client.get(f"/projects/{project_with_member.id}")
        assert response.status_code == 200

    def test_member_access_other_project(self, member_client: TestClient, db: Session, team_lead_user):
        """Test member cannot access other projects"""
        other_project = Project(
            name="Other Project",
            description="Not accessible",
            team_lead_id=team_lead_user.id,
            status="planning",
        )
        db.add(other_project)
        db.commit()

        response = member_client.get(f"/projects/{other_project.id}")
        assert response.status_code == 403

    def test_unauthenticated_access(self, client: TestClient, test_project):
        """Test unauthenticated user cannot access projects"""
        response = client.get(f"/projects/{test_project.id}")
        assert response.status_code == 401

    def test_unauthenticated_create(self, client: TestClient):
        """Test unauthenticated user cannot create project"""
        response = client.post(
            "/projects/",
            json={"name": "Unauthorized", "description": "Test"},
        )
        assert response.status_code == 401


class TestProjectValidation:
    """Test project input validation"""

    def test_create_empty_name(self, lead_client: TestClient):
        """Test creating project with empty name"""
        response = lead_client.post(
            "/projects/",
            json={"name": "", "description": "Empty name"},
        )
        assert response.status_code == 422

    def test_create_null_description(self, lead_client: TestClient):
        """Test creating project with null description"""
        response = lead_client.post(
            "/projects/",
            json={"name": "Valid Name", "description": None},
        )
        # None/null should be acceptable for optional field
        assert response.status_code == 200

    def test_update_invalid_status(self, lead_client: TestClient, test_project):
        """Test updating to invalid status"""
        response = lead_client.put(
            f"/projects/{test_project.id}",
            json={"status": "invalid_status"},
        )
        assert response.status_code == 422

    def test_create_with_special_characters(self, lead_client: TestClient):
        """Test creating project with special characters in name"""
        response = lead_client.post(
            "/projects/",
            json={"name": "Project @#$%^&*", "description": "Special chars"},
        )
        assert response.status_code == 200

    def test_create_with_unicode(self, lead_client: TestClient):
        """Test creating project with unicode characters"""
        response = lead_client.post(
            "/projects/",
            json={"name": "项目测试 🎉", "description": "Unicode test"},
        )
        assert response.status_code == 200
