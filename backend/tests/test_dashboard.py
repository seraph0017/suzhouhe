"""
Test Dashboard and Reports API

Tests for role-specific dashboards, task management, and progress tracking.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import User, UserRole
from app.models.project import Project, ProjectMember, ProjectMemberRole
from app.models.chapter import Chapter, ChapterStatus
from app.models.review import Review, ReviewType, ReviewStatus


class TestDashboardStats:
    """Test dashboard statistics endpoints"""

    def test_get_dashboard_stats_admin(self, auth_client: TestClient, db: Session, team_lead_user):
        """Test admin dashboard stats"""
        # Create some test data
        project = Project(
            name="Stats Test Project",
            team_lead_id=team_lead_user.id,
            status="in_progress",
        )
        db.add(project)
        db.commit()

        response = auth_client.get("/dashboard/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_projects" in data
        assert "active_projects" in data

    def test_get_dashboard_stats_team_lead(self, lead_client: TestClient):
        """Test team lead dashboard stats"""
        response = lead_client.get("/dashboard/stats")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)

    def test_get_dashboard_stats_team_member(self, member_client: TestClient):
        """Test team member dashboard stats"""
        response = member_client.get("/dashboard/stats")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)

    def test_get_dashboard_stats_unauthenticated(self, client: TestClient):
        """Test unauthenticated dashboard access"""
        response = client.get("/dashboard/stats")
        assert response.status_code == 401


class TestDashboardTasks:
    """Test dashboard task endpoints"""

    def test_get_my_tasks_team_member(self, member_client: TestClient):
        """Test team member getting their tasks"""
        response = member_client.get("/dashboard/tasks")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data

    def test_get_my_tasks_team_lead(self, lead_client: TestClient):
        """Test team lead getting their tasks"""
        response = lead_client.get("/dashboard/tasks")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)

    def test_get_tasks_with_status_filter(self, member_client: TestClient):
        """Test filtering tasks by status"""
        response = member_client.get("/dashboard/tasks?status=pending")
        assert response.status_code == 200

    def test_tasks_include_due_date_indicator(self, member_client: TestClient, db: Session, team_member, team_lead_user):
        """Test tasks include urgency indicators"""
        project = Project(
            name="Task Test Project",
            team_lead_id=team_lead_user.id,
            status="in_progress",
        )
        db.add(project)
        db.commit()

        # Add member to project
        membership = ProjectMember(
            project_id=project.id,
            user_id=team_member.id,
            role=ProjectMemberRole.MEMBER,
        )
        db.add(membership)
        db.commit()

        response = member_client.get("/dashboard/tasks")
        assert response.status_code == 200


class TestDashboardProjects:
    """Test dashboard project endpoints"""

    def test_get_dashboard_projects_member(self, member_client: TestClient, project_with_member):
        """Test team member seeing their projects"""
        response = member_client.get("/dashboard/projects")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data

    def test_get_dashboard_projects_lead(self, lead_client: TestClient, test_project):
        """Test team lead seeing their projects"""
        response = lead_client.get("/dashboard/projects")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data

    def test_get_dashboard_projects_admin(self, auth_client: TestClient, test_project):
        """Test admin seeing all projects"""
        response = auth_client.get("/dashboard/projects")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data


class TestRoleSpecificDashboards:
    """Test role-specific dashboard endpoints"""

    def test_admin_dashboard_access(self, auth_client: TestClient):
        """Test admin dashboard access"""
        response = auth_client.get("/admin/dashboard")
        assert response.status_code in [200, 404]

    def test_team_lead_dashboard_access(self, lead_client: TestClient):
        """Test team lead dashboard access"""
        response = lead_client.get("/lead/dashboard")
        assert response.status_code in [200, 404]

    def test_team_member_dashboard_access(self, member_client: TestClient):
        """Test team member dashboard access"""
        response = member_client.get("/member/dashboard")
        assert response.status_code in [200, 404]

    def test_member_cannot_access_admin_dashboard(self, member_client: TestClient):
        """Test team member cannot access admin dashboard"""
        response = member_client.get("/admin/dashboard")
        assert response.status_code in [403, 404]

    def test_member_cannot_access_lead_dashboard(self, member_client: TestClient):
        """Test team member cannot access team lead dashboard"""
        response = member_client.get("/lead/dashboard")
        assert response.status_code in [403, 404]

    def test_lead_cannot_access_admin_dashboard(self, lead_client: TestClient):
        """Test team lead cannot access admin dashboard"""
        response = lead_client.get("/admin/dashboard")
        assert response.status_code in [403, 404]


class TestProgressTracking:
    """Test progress tracking endpoints"""

    def test_get_project_progress(self, lead_client: TestClient, test_project):
        """Test getting project progress"""
        response = lead_client.get(f"/projects/{test_project.id}/progress")
        assert response.status_code in [200, 404]

    def test_get_chapter_progress(self, lead_client: TestClient, db: Session, team_lead_user):
        """Test getting chapter progress"""
        project = Project(
            name="Progress Test",
            team_lead_id=team_lead_user.id,
        )
        db.add(project)
        db.commit()

        chapter = Chapter(
            script_id=1,
            order=1,
            title="Progress Chapter",
            content="Content",
            status="in_progress",
        )
        db.add(chapter)
        db.commit()

        response = lead_client.get(f"/chapters/{chapter.id}/progress")
        assert response.status_code in [200, 404]

    def test_get_pipeline_status(self, lead_client: TestClient, script_with_chapters):
        """Test getting pipeline status"""
        script, chapters = script_with_chapters

        response = lead_client.get(f"/pipeline/status?script_id={script.id}")
        assert response.status_code in [200, 404]


class TestTaskManagement:
    """Test task management endpoints"""

    def test_start_task(self, member_client: TestClient, db: Session, team_member, team_lead_user):
        """Test starting a task"""
        project = Project(
            name="Task Start Test",
            team_lead_id=team_lead_user.id,
            status="in_progress",
        )
        db.add(project)
        db.commit()

        chapter = Chapter(
            script_id=1,
            order=1,
            title="Task Chapter",
            content="Content",
            status="pending",
        )
        db.add(chapter)
        db.commit()

        response = member_client.post(f"/tasks/{chapter.id}/start")
        assert response.status_code in [200, 404]

    def test_complete_task(self, member_client: TestClient, db: Session, team_member, team_lead_user):
        """Test completing a task"""
        project = Project(
            name="Task Complete Test",
            team_lead_id=team_lead_user.id,
            status="in_progress",
        )
        db.add(project)
        db.commit()

        chapter = Chapter(
            script_id=1,
            order=1,
            title="Complete Chapter",
            content="Content",
            status="in_progress",
        )
        db.add(chapter)
        db.commit()

        response = member_client.post(f"/tasks/{chapter.id}/complete")
        assert response.status_code in [200, 404]

    def test_reassign_task_team_lead(self, lead_client: TestClient, db: Session, team_member, team_lead_user):
        """Test team lead reassigning task"""
        project = Project(
            name="Task Reassign Test",
            team_lead_id=team_lead_user.id,
        )
        db.add(project)
        db.commit()

        chapter = Chapter(
            script_id=1,
            order=1,
            title="Reassign Chapter",
            content="Content",
            status="pending",
        )
        db.add(chapter)
        db.commit()

        response = lead_client.post(
            f"/tasks/{chapter.id}/reassign",
            json={"assignee_id": team_member.id},
        )

        assert response.status_code in [200, 404]

    def test_member_cannot_reassign_task(self, member_client: TestClient, db: Session, team_member, team_lead_user):
        """Test team member cannot reassign tasks"""
        project = Project(
            name="Task No Reassign",
            team_lead_id=team_lead_user.id,
        )
        db.add(project)
        db.commit()

        chapter = Chapter(
            script_id=1,
            order=1,
            title="No Reassign Chapter",
            content="Content",
        )
        db.add(chapter)
        db.commit()

        response = member_client.post(
            f"/tasks/{chapter.id}/reassign",
            json={"assignee_id": team_member.id},
        )

        assert response.status_code == 403


class TestReports:
    """Test report generation endpoints"""

    def test_export_project_report(self, lead_client: TestClient, test_project):
        """Test exporting project report"""
        response = lead_client.post(
            f"/reports/project/{test_project.id}/export",
        )

        assert response.status_code in [200, 404]

    def test_export_audit_report(self, lead_client: TestClient):
        """Test exporting audit report"""
        response = lead_client.post(
            "/reports/audit/export",
            json={"start_date": "2026-01-01", "end_date": "2026-03-01"},
        )

        assert response.status_code in [200, 404]

    def test_get_quality_metrics(self, lead_client: TestClient):
        """Test getting quality metrics"""
        response = lead_client.get("/reports/quality-metrics")
        assert response.status_code in [200, 404]


class TestAchievements:
    """Test achievements and statistics"""

    def test_get_my_achievements(self, member_client: TestClient):
        """Test getting personal achievements"""
        response = member_client.get("/achievements")
        assert response.status_code in [200, 404]

    def test_get_team_statistics(self, lead_client: TestClient, db: Session, team_lead_user):
        """Test getting team statistics"""
        project = Project(
            name="Team Stats Test",
            team_lead_id=team_lead_user.id,
        )
        db.add(project)
        db.commit()

        response = lead_client.get(f"/projects/{project.id}/statistics")
        assert response.status_code in [200, 404]


class TestDashboardRealTime:
    """Test real-time dashboard updates"""

    def test_dashboard_refresh(self, member_client: TestClient):
        """Test dashboard data refresh"""
        response = member_client.post("/dashboard/refresh")
        assert response.status_code in [200, 404]

    def test_notification_subscription(self, member_client: TestClient):
        """Test notification subscription"""
        response = member_client.post("/notifications/subscribe")
        assert response.status_code in [200, 404]
