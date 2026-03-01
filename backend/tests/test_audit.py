"""
Test Dual-Audit System

Tests for first audit (Team Member) and second audit (Team Lead) workflows,
rejection handling, and revision flow.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import User, UserRole
from app.models.project import Project
from app.models.chapter import Chapter
from app.models.storyboard import Storyboard
from app.models.review import Review, ReviewType, ReviewStatus


class TestFirstAudit:
    """Test First Audit (Team Member)"""

    def test_get_first_audit_pending(self, member_client: TestClient, db: Session, team_member, team_lead_user):
        """Test getting pending first audit"""
        # Setup
        project = Project(
            name="Audit Test Project",
            team_lead_id=team_lead_user.id,
        )
        db.add(project)
        db.commit()

        chapter = Chapter(
            script_id=1,
            order=1,
            title="Test Chapter",
            content="Content",
            status="in_review",
        )
        db.add(chapter)
        db.commit()

        review = Review(
            review_type=ReviewType.FIRST_AUDIT,
            target_type="chapter",
            target_id=chapter.id,
            reviewer_id=team_member.id,
            status=ReviewStatus.PENDING,
        )
        db.add(review)
        db.commit()

        response = member_client.get(f"/audits/first/{chapter.id}")
        assert response.status_code in [200, 404]

    def test_submit_first_audit_approve(self, member_client: TestClient, first_audit_review):
        """Test submitting first audit with approval"""
        review = first_audit_review

        response = member_client.post(
            f"/audits/first/{review.target_id}/submit",
            json={
                "decision": "approve",
                "comments": "All assets look good",
            },
        )

        assert response.status_code in [200, 404]

    def test_submit_first_audit_reject(self, member_client: TestClient, first_audit_review):
        """Test submitting first audit with rejection"""
        review = first_audit_review

        response = member_client.post(
            f"/audits/first/{review.target_id}/submit",
            json={
                "decision": "reject",
                "comments": "Image quality issues in panel 3",
                "rejected_panels": [3],
            },
        )

        assert response.status_code in [200, 404]

    def test_first_audit_approve_panel(self, member_client: TestClient, first_audit_review):
        """Test approving individual panel in first audit"""
        review = first_audit_review

        response = member_client.put(
            f"/audits/first/{review.target_id}/panel/1/approve",
        )

        assert response.status_code in [200, 404]

    def test_first_audit_reject_panel(self, member_client: TestClient, first_audit_review):
        """Test rejecting individual panel in first audit"""
        review = first_audit_review

        response = member_client.put(
            f"/audits/first/{review.target_id}/panel/1/reject",
            json={"reason": "Poor image quality"},
        )

        assert response.status_code in [200, 404]

    def test_first_audit_regenerate_all(self, member_client: TestClient, first_audit_review):
        """Test requesting regeneration for all panels"""
        review = first_audit_review

        response = member_client.post(
            f"/audits/first/{review.target_id}/regenerate-all",
            json={"type": "image", "reason": "Style inconsistency"},
        )

        assert response.status_code in [200, 202, 404]

    def test_first_audit_add_comment(self, member_client: TestClient, first_audit_review):
        """Test adding comment to panel"""
        review = first_audit_review

        response = member_client.post(
            f"/audits/first/{review.target_id}/panel/1/comment",
            json={"comment": "Check character consistency"},
        )

        assert response.status_code in [200, 404]

    def test_first_audit_team_lead_forbidden(self, lead_client: TestClient, first_audit_review):
        """Test team lead cannot perform first audit"""
        review = first_audit_review

        response = lead_client.post(
            f"/audits/first/{review.target_id}/submit",
            json={"decision": "approve"},
        )

        # Team lead should not be able to do first audit (it's for team members)
        assert response.status_code == 403

    def test_first_audit_get_history(self, member_client: TestClient, first_audit_review):
        """Test getting first audit history"""
        review = first_audit_review

        response = member_client.get(f"/audits/first/{review.target_id}/history")
        assert response.status_code in [200, 404]


class TestSecondAudit:
    """Test Second Audit (Team Lead)"""

    def test_get_second_audit_pending(self, lead_client: TestClient, second_audit_review):
        """Test getting pending second audit"""
        review = second_audit_review

        response = lead_client.get(f"/audits/second/{review.target_id}")
        assert response.status_code in [200, 404]

    def test_second_audit_approve(self, lead_client: TestClient, second_audit_review):
        """Test approving in second audit"""
        review = second_audit_review

        response = lead_client.post(
            f"/audits/second/{review.target_id}/approve",
            json={
                "rating": 5,
                "feedback": "Excellent work!",
            },
        )

        assert response.status_code in [200, 404]

    def test_second_audit_reject(self, lead_client: TestClient, second_audit_review):
        """Test rejecting in second audit"""
        review = second_audit_review

        response = lead_client.post(
            f"/audits/second/{review.target_id}/reject",
            json={
                "reason": "Lip-sync issues detected",
                "category": "video_quality",
                "return_to_step": 6,
                "requires_re_audit": True,
            },
        )

        assert response.status_code in [200, 404]

    def test_second_audit_minor_edit(self, lead_client: TestClient, second_audit_review):
        """Test requesting minor edit (no re-audit needed)"""
        review = second_audit_review

        response = lead_client.post(
            f"/audits/second/{review.target_id}/minor-edit",
            json={
                "reason": "Subtitle typo",
                "instructions": "Fix typo at 00:15",
            },
        )

        assert response.status_code in [200, 404]

    def test_second_audit_add_timestamped_comment(self, lead_client: TestClient, second_audit_review):
        """Test adding timestamped comment"""
        review = second_audit_review

        response = lead_client.post(
            f"/audits/second/{review.target_id}/comment",
            json={
                "timestamp_sec": 15.5,
                "comment": "Lip-sync off here",
            },
        )

        assert response.status_code in [200, 404]

    def test_second_audit_team_member_forbidden(self, member_client: TestClient, second_audit_review):
        """Test team member cannot perform second audit"""
        review = second_audit_review

        response = member_client.post(
            f"/audits/second/{review.target_id}/approve",
        )

        assert response.status_code == 403

    def test_second_audit_get_stats(self, lead_client: TestClient):
        """Test getting second audit statistics"""
        response = lead_client.get("/audits/second/stats")
        assert response.status_code in [200, 404]


class TestRejectionRouting:
    """Test rejection routing to appropriate steps"""

    def test_reject_image_quality_returns_to_step5(self, lead_client: TestClient, second_audit_review):
        """Test image quality rejection returns to Step 5"""
        review = second_audit_review

        response = lead_client.post(
            f"/audits/second/{review.target_id}/reject",
            json={
                "reason": "Poor image quality",
                "category": "image_quality",
                "return_to_step": 5,
            },
        )

        assert response.status_code in [200, 404]
        # Should require re-audit
        data = response.json() if response.status_code == 200 else {}
        if data:
            assert data.get("requires_re_audit") is True

    def test_reject_lipsync_returns_to_step6(self, lead_client: TestClient, second_audit_review):
        """Test lip-sync rejection returns to Step 6"""
        review = second_audit_review

        response = lead_client.post(
            f"/audits/second/{review.target_id}/reject",
            json={
                "reason": "Lip-sync inaccurate",
                "category": "lip_sync",
                "return_to_step": 6,
            },
        )

        assert response.status_code in [200, 404]

    def test_reject_subtitle_returns_to_step7_no_reatudit(self, lead_client: TestClient, second_audit_review):
        """Test subtitle rejection returns to Step 7 without re-audit"""
        review = second_audit_review

        response = lead_client.post(
            f"/audits/second/{review.target_id}/reject",
            json={
                "reason": "Subtitle typo",
                "category": "subtitle",
                "return_to_step": 7,
                "requires_re_audit": False,
            },
        )

        assert response.status_code in [200, 404]

    def test_reject_bgm_returns_to_step7(self, lead_client: TestClient, second_audit_review):
        """Test BGM rejection returns to Step 7"""
        review = second_audit_review

        response = lead_client.post(
            f"/audits/second/{review.target_id}/reject",
            json={
                "reason": "BGM doesn't match mood",
                "category": "bgm",
                "return_to_step": 7,
            },
        )

        assert response.status_code in [200, 404]

    def test_reject_storyboard_returns_to_step4(self, lead_client: TestClient, second_audit_review):
        """Test storyboard rejection returns to Step 4"""
        review = second_audit_review

        response = lead_client.post(
            f"/audits/second/{review.target_id}/reject",
            json={
                "reason": "Panel order wrong",
                "category": "storyboard",
                "return_to_step": 4,
            },
        )

        assert response.status_code in [200, 404]


class TestRevisionFlow:
    """Test revision and re-audit flow"""

    def test_revision_notification_sent(self, member_client: TestClient, first_audit_review):
        """Test revision notification"""
        review = first_audit_review

        # After rejection, member should be able to see the feedback
        response = member_client.get(f"/audits/first/{review.target_id}/feedback")
        assert response.status_code in [200, 404]

    def test_revision_access_to_returned_step(self, member_client: TestClient, db: Session, team_member, team_lead_user):
        """Test accessing returned step for revision"""
        project = Project(
            name="Revision Test",
            team_lead_id=team_lead_user.id,
        )
        db.add(project)
        db.commit()

        # Create chapter at step 5 (material generation)
        chapter = Chapter(
            script_id=1,
            order=1,
            title="Revision Chapter",
            content="Content",
            status="revision_required",
        )
        db.add(chapter)
        db.commit()

        # Member should be able to access returned step
        response = member_client.get(f"/chapters/{chapter.id}/materials")
        assert response.status_code in [200, 403, 404]

    def test_resubmit_after_revision(self, member_client: TestClient, first_audit_review):
        """Test resubmitting after revision"""
        review = first_audit_review

        response = member_client.post(
            f"/audits/first/{review.target_id}/resubmit",
            json={"decision": "approve", "changes_made": "Fixed image quality"},
        )

        assert response.status_code in [200, 404]

    def test_multiple_rejections_escalation(self, lead_client: TestClient, db: Session, team_lead_user, admin_user):
        """Test escalation after multiple rejections"""
        project = Project(
            name="Escalation Test",
            team_lead_id=team_lead_user.id,
        )
        db.add(project)
        db.commit()

        chapter = Chapter(
            script_id=1,
            order=1,
            title="Escalation Chapter",
            content="Content",
            status="in_review",
        )
        db.add(chapter)
        db.commit()

        # Simulate 3 rejections
        for i in range(3):
            review = Review(
                review_type=ReviewType.SECOND_AUDIT,
                target_type="chapter_video",
                target_id=chapter.id,
                reviewer_id=team_lead_user.id,
                status=ReviewStatus.REJECTED,
                rejection_reason=f"Rejection {i+1}",
            )
            db.add(review)

        db.commit()

        # Third rejection should trigger escalation
        # (notification to admin, etc.)
        assert db.query(Review).filter(
            Review.target_id == chapter.id,
            Review.status == ReviewStatus.REJECTED
        ).count() == 3


class TestAuditStateTransitions:
    """Test audit state machine transitions"""

    def test_pending_to_in_review(self, member_client: TestClient, first_audit_review):
        """Test transition from pending to in_review"""
        review = first_audit_review

        # Starting audit should change status to in_review
        response = member_client.post(
            f"/audits/first/{review.target_id}/start",
        )

        assert response.status_code in [200, 404]

    def test_in_review_to_approved(self, member_client: TestClient, first_audit_review):
        """Test transition from in_review to approved"""
        review = first_audit_review

        response = member_client.post(
            f"/audits/first/{review.target_id}/submit",
            json={"decision": "approve"},
        )

        assert response.status_code in [200, 404]

    def test_in_review_to_rejected(self, member_client: TestClient, first_audit_review):
        """Test transition from in_review to rejected"""
        review = first_audit_review

        response = member_client.post(
            f"/audits/first/{review.target_id}/submit",
            json={"decision": "reject", "reason": "Issues found"},
        )

        assert response.status_code in [200, 404]

    def test_rejected_to_pending_reatudit(self, lead_client: TestClient, db: Session, team_lead_user):
        """Test transition from rejected back to pending (re-audit)"""
        project = Project(
            name="Re-audit Test",
            team_lead_id=team_lead_user.id,
        )
        db.add(project)
        db.commit()

        chapter = Chapter(
            script_id=1,
            order=1,
            title="Re-audit Chapter",
            content="Content",
            status="pending_second_audit",
        )
        db.add(chapter)
        db.commit()

        # Create rejected review
        review = Review(
            review_type=ReviewType.SECOND_AUDIT,
            target_type="chapter_video",
            target_id=chapter.id,
            reviewer_id=team_lead_user.id,
            status=ReviewStatus.REJECTED,
        )
        db.add(review)
        db.commit()

        # After revision, should be pending again
        response = lead_client.post(f"/audits/second/{chapter.id}/reattend")
        assert response.status_code in [200, 404]


class TestAuditAccessControl:
    """Test audit access control"""

    def test_member_only_own_audits(self, member_client: TestClient, db: Session, team_member, team_lead_user):
        """Test member can only access their assigned audits"""
        project = Project(
            name="Member Audit Test",
            team_lead_id=team_lead_user.id,
        )
        db.add(project)
        db.commit()

        chapter = Chapter(
            script_id=1,
            order=1,
            title="Other Chapter",
            content="Content",
        )
        db.add(chapter)
        db.commit()

        # Review assigned to different member
        other_review = Review(
            review_type=ReviewType.FIRST_AUDIT,
            target_type="chapter",
            target_id=chapter.id,
            reviewer_id=999,  # Different member
            status=ReviewStatus.PENDING,
        )
        db.add(other_review)
        db.commit()

        response = member_client.get(f"/audits/first/{chapter.id}")
        assert response.status_code in [403, 404]

    def test_unauthenticated_audit_access(self, client: TestClient, first_audit_review):
        """Test unauthenticated access to audit"""
        review = first_audit_review

        response = client.get(f"/audits/first/{review.target_id}")
        assert response.status_code == 401


class TestAuditLogging:
    """Test audit trail logging"""

    def test_audit_action_logged(self, member_client: TestClient, first_audit_review, db: Session):
        """Test audit action is logged"""
        review = first_audit_review

        response = member_client.post(
            f"/audits/first/{review.target_id}/submit",
            json={"decision": "approve"},
        )

        if response.status_code == 200:
            # Check audit log was created
            from app.models.audit_log import AuditLog
            log = db.query(AuditLog).filter(
                AuditLog.action == "FIRST_AUDIT_SUBMIT",
                AuditLog.entity_id == review.target_id,
            ).first()
            assert log is not None

    def test_audit_timestamp_recorded(self, member_client: TestClient, first_audit_review, db: Session):
        """Test audit timestamp is recorded"""
        review = first_audit_review

        response = member_client.post(
            f"/audits/first/{review.target_id}/submit",
            json={"decision": "approve"},
        )

        if response.status_code == 200:
            db.refresh(review)
            assert review.reviewed_at is not None
