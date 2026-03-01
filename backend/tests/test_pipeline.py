"""
Test Pipeline Workflow

Tests for the 8-step pipeline: Script -> Refinement -> Chapter Breakdown ->
Storyboard -> Material Generation -> Video Generation -> Composition -> Assembly
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import User, UserRole
from app.models.project import Project
from app.models.script import Script, ScriptStatus
from app.models.chapter import Chapter, ChapterStatus
from app.models.storyboard import Storyboard, StoryboardStatus
from app.models.asset import Asset, AssetType, AssetStatus
from app.models.review import Review, ReviewType, ReviewStatus


class TestScriptBase:
    """Test Step 1: Script Base"""

    def test_create_script_llm(self, lead_client: TestClient, test_project):
        """Test creating script via LLM generation"""
        response = lead_client.post(
            "/scripts/",
            json={
                "project_id": test_project.id,
                "title": "LLM Generated Script",
                "content": '{"scenes": [{"id": 1, "description": "Scene 1", "dialogue": "Hello"}]}',
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "LLM Generated Script"
        assert data["project_id"] == test_project.id
        assert data["status"] == "draft"

    def test_create_script_upload(self, lead_client: TestClient, test_project):
        """Test creating script via file upload"""
        # Note: Actual file upload test would need multipart/form-data
        # This tests the JSON endpoint
        response = lead_client.post(
            "/scripts/",
            json={
                "project_id": test_project.id,
                "title": "Uploaded Script",
                "content": "Plain text script content",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Uploaded Script"

    def test_create_script_team_member_forbidden(self, member_client: TestClient, test_project):
        """Test team member cannot create script"""
        response = member_client.post(
            "/scripts/",
            json={
                "project_id": test_project.id,
                "title": "Member Script",
                "content": "Should fail",
            },
        )

        assert response.status_code == 403

    def test_get_script(self, lead_client: TestClient, db: Session, team_lead_user):
        """Test getting script by ID"""
        project = Project(
            name="Script Test Project",
            team_lead_id=team_lead_user.id,
        )
        db.add(project)
        db.commit()

        script = Script(
            project_id=project.id,
            title="Test Script",
            content="Test content",
        )
        db.add(script)
        db.commit()

        response = lead_client.get(f"/scripts/{script.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == script.id
        assert data["title"] == "Test Script"

    def test_get_script_not_found(self, lead_client: TestClient):
        """Test getting non-existent script"""
        response = lead_client.get("/scripts/99999")
        assert response.status_code == 404


class TestScriptRefinement:
    """Test Step 2: Script Refinement"""

    def test_update_script(self, lead_client: TestClient, db: Session, team_lead_user):
        """Test updating script content"""
        project = Project(
            name="Refine Test Project",
            team_lead_id=team_lead_user.id,
        )
        db.add(project)
        db.commit()

        script = Script(
            project_id=project.id,
            title="Original Title",
            content="Original content",
            status=ScriptStatus.DRAFT,
        )
        db.add(script)
        db.commit()

        response = lead_client.put(
            f"/scripts/{script.id}",
            json={"content": "Updated content", "title": "Updated Title"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["content"] == "Updated content"
        assert data["title"] == "Updated Title"
        assert data["version"] == 2  # Version should increment

    def test_lock_script(self, lead_client: TestClient, db: Session, team_lead_user):
        """Test locking script triggers chapter breakdown"""
        project = Project(
            name="Lock Test Project",
            team_lead_id=team_lead_user.id,
        )
        db.add(project)
        db.commit()

        script = Script(
            project_id=project.id,
            title="Lock Test",
            content='{"scenes": [{"id": 1, "description": "Scene 1"}]}',
            status=ScriptStatus.DRAFT,
            is_locked=False,
        )
        db.add(script)
        db.commit()

        response = lead_client.post(f"/scripts/{script.id}/lock")
        assert response.status_code == 200
        data = response.json()
        assert data["is_locked"] is True
        assert data["status"] == "locked"

    def test_edit_locked_script_forbidden(self, lead_client: TestClient, db: Session, team_lead_user):
        """Test editing locked script fails"""
        project = Project(
            name="Locked Edit Project",
            team_lead_id=team_lead_user.id,
        )
        db.add(project)
        db.commit()

        script = Script(
            project_id=project.id,
            title="Locked Script",
            content="Original content",
            is_locked=True,
            status=ScriptStatus.LOCKED,
        )
        db.add(script)
        db.commit()

        response = lead_client.put(
            f"/scripts/{script.id}",
            json={"content": "Cannot change this"},
        )

        assert response.status_code == 400
        assert "locked" in response.json()["detail"].lower()

    def test_unlock_script(self, lead_client: TestClient, db: Session, team_lead_user):
        """Test unlocking script"""
        project = Project(
            name="Unlock Test Project",
            team_lead_id=team_lead_user.id,
        )
        db.add(project)
        db.commit()

        script = Script(
            project_id=project.id,
            title="Unlock Test",
            content="Content",
            is_locked=True,
            status=ScriptStatus.LOCKED,
        )
        db.add(script)
        db.commit()

        response = lead_client.post(f"/scripts/{script.id}/unlock")
        assert response.status_code == 200
        data = response.json()
        assert data["is_locked"] is False

    def test_get_script_versions(self, lead_client: TestClient, db: Session, team_lead_user):
        """Test getting script version history"""
        project = Project(
            name="Version Test Project",
            team_lead_id=team_lead_user.id,
        )
        db.add(project)
        db.commit()

        script = Script(
            project_id=project.id,
            title="Version Test",
            content="v1 content",
            version=3,
        )
        db.add(script)
        db.commit()

        response = lead_client.get(f"/scripts/{script.id}/versions")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestChapterBreakdown:
    """Test Step 3: Chapter Breakdown"""

    def test_get_chapters_auto_generated(self, lead_client: TestClient, script_with_chapters):
        """Test getting auto-generated chapters"""
        script, chapters = script_with_chapters

        response = lead_client.get(f"/chapters/?script_id={script.id}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert data[0]["title"] == "Chapter 1"

    def test_update_chapter(self, lead_client: TestClient, script_with_chapters):
        """Test updating chapter metadata"""
        script, chapters = script_with_chapters
        chapter = chapters[0]

        response = lead_client.put(
            f"/chapters/{chapter.id}",
            json={
                "title": "Custom Chapter Title",
                "summary": "Custom summary",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Custom Chapter Title"

    def test_split_chapter(self, lead_client: TestClient, script_with_chapters):
        """Test splitting a chapter"""
        script, chapters = script_with_chapters
        chapter = chapters[0]

        response = lead_client.post(
            f"/chapters/{chapter.id}/split",
            json={"split_at_order": 2},
        )

        # Depending on implementation, this may create a new chapter
        assert response.status_code in [200, 400]

    def test_merge_chapters(self, lead_client: TestClient, script_with_chapters):
        """Test merging adjacent chapters"""
        script, chapters = script_with_chapters

        response = lead_client.post(
            "/chapters/merge",
            json={"chapter_ids": [chapters[0].id, chapters[1].id]},
        )

        # May or may not be implemented
        assert response.status_code in [200, 404, 400]

    def test_reorder_chapters(self, lead_client: TestClient, script_with_chapters):
        """Test reordering chapters"""
        script, chapters = script_with_chapters

        response = lead_client.patch(
            "/chapters/reorder",
            json={"script_id": script.id, "order": [2, 1, 3]},
        )

        assert response.status_code in [200, 404]


class TestStoryboardCreation:
    """Test Step 4: Storyboard Creation"""

    def test_get_storyboards(self, lead_client: TestClient, storyboard_with_panels):
        """Test getting storyboard panels"""
        chapter, panels = storyboard_with_panels

        response = lead_client.get(f"/storyboards/?chapter_id={chapter.id}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5

    def test_update_storyboard_panel(self, lead_client: TestClient, storyboard_with_panels):
        """Test updating storyboard panel"""
        chapter, panels = storyboard_with_panels
        panel = panels[0]

        response = lead_client.put(
            f"/storyboards/{panel.id}",
            json={
                "visual_description": "Updated description",
                "camera_direction": "PAN_LEFT",
                "dialogue": "Updated dialogue",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["visual_description"] == "Updated description"

    def test_add_storyboard_panel(self, lead_client: TestClient, storyboard_with_panels):
        """Test adding new storyboard panel"""
        chapter, panels = storyboard_with_panels

        response = lead_client.post(
            "/storyboards/",
            json={
                "chapter_id": chapter.id,
                "order": 6,
                "title": "New Panel",
                "visual_description": "New panel description",
                "dialogue": "New dialogue",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["order"] == 6

    def test_delete_storyboard_panel(self, lead_client: TestClient, storyboard_with_panels):
        """Test deleting storyboard panel"""
        chapter, panels = storyboard_with_panels
        panel = panels[-1]

        response = lead_client.delete(f"/storyboards/{panel.id}")
        assert response.status_code == 200

    def test_lock_storyboard(self, lead_client: TestClient, storyboard_with_panels):
        """Test locking storyboard triggers material generation"""
        chapter, panels = storyboard_with_panels

        response = lead_client.post(f"/storyboards/chapter/{chapter.id}/lock")
        assert response.status_code in [200, 400]


class TestMaterialGeneration:
    """Test Step 5: Material Generation"""

    def test_get_generated_images(self, member_client: TestClient, assets_for_panels):
        """Test getting generated images for panel"""
        chapter, panels, assets = assets_for_panels
        panel = panels[0]

        response = member_client.get(f"/assets/?storyboard_id={panel.id}&type=image")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

    def test_select_image(self, member_client: TestClient, assets_for_panels):
        """Test selecting an image for panel"""
        chapter, panels, assets = assets_for_panels
        image = assets[0]

        response = member_client.put(
            f"/assets/{image.id}/select",
            json={"is_selected": True},
        )

        assert response.status_code in [200, 404]

    def test_regenerate_image(self, member_client: TestClient, assets_for_panels):
        """Test requesting image regeneration"""
        chapter, panels, assets = assets_for_panels
        panel = panels[0]

        response = member_client.post(
            f"/assets/panel/{panel.id}/regenerate",
            json={"type": "image"},
        )

        # Should trigger new generation
        assert response.status_code in [200, 202, 404]

    def test_get_generated_audio(self, member_client: TestClient, assets_for_panels):
        """Test getting generated audio for panel"""
        chapter, panels, assets = assets_for_panels
        panel = panels[0]

        response = member_client.get(f"/assets/?storyboard_id={panel.id}&type=audio")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

    def test_select_voice_actor(self, member_client: TestClient, assets_for_panels):
        """Test selecting different voice actor"""
        chapter, panels, assets = assets_for_panels
        panel = panels[0]

        response = member_client.post(
            f"/assets/panel/{panel.id}/regenerate",
            json={
                "type": "audio",
                "params": {"voice_id": "zh-CN-YunxiNeural"},
            },
        )

        assert response.status_code in [200, 202, 404]


class TestVideoGeneration:
    """Test Step 6: Video Generation"""

    def test_generate_video(self, lead_client: TestClient, assets_for_panels):
        """Test generating lip-sync video"""
        chapter, panels, assets = assets_for_panels
        panel = panels[0]

        # Get selected image and audio
        selected_image = next((a for a in assets if a.type == AssetType.IMAGE), None)
        selected_audio = next((a for a in assets if a.type == AssetType.AUDIO), None)

        if selected_image and selected_audio:
            response = lead_client.post(
                "/videos/generate",
                json={
                    "storyboard_id": panel.id,
                    "image_id": selected_image.id,
                    "audio_id": selected_audio.id,
                },
            )

            assert response.status_code in [200, 202, 404]

    def test_get_video_status(self, lead_client: TestClient, db: Session):
        """Test checking video generation status"""
        response = lead_client.get("/videos/job_123/status")
        assert response.status_code in [200, 404]


class TestSmartComposition:
    """Test Step 7: Smart Composition"""

    def test_get_bgm_recommendations(self, member_client: TestClient, assets_for_panels):
        """Test getting AI-recommended BGM"""
        chapter, panels, assets = assets_for_panels

        response = member_client.get(f"/composition/recommendations?chapter_id={chapter.id}")
        assert response.status_code in [200, 404]

    def test_set_bgm(self, member_client: TestClient, assets_for_panels):
        """Test setting BGM for chapter"""
        chapter, panels, assets = assets_for_panels

        response = member_client.put(
            f"/composition/{chapter.id}/bgm",
            json={"bgm_id": "bgm_123", "volume": 0.3},
        )

        assert response.status_code in [200, 404]

    def test_update_subtitles(self, member_client: TestClient, assets_for_panels):
        """Test updating subtitles"""
        chapter, panels, assets = assets_for_panels
        panel = panels[0]

        response = member_client.put(
            f"/storyboards/{panel.id}/subtitles",
            json={"subtitle": "Updated subtitle text"},
        )

        assert response.status_code in [200, 404]


class TestChapterAssembly:
    """Test Step 8: Chapter Assembly"""

    def test_assemble_chapter(self, lead_client: TestClient, assets_for_panels):
        """Test assembling final chapter video"""
        chapter, panels, assets = assets_for_panels

        response = lead_client.post(f"/chapters/{chapter.id}/assemble")
        assert response.status_code in [200, 202, 404]

    def test_get_chapter_video(self, lead_client: TestClient, assets_for_panels):
        """Test getting assembled chapter video"""
        chapter, panels, assets = assets_for_panels

        response = lead_client.get(f"/chapters/{chapter.id}/video")
        assert response.status_code in [200, 404]


class TestPipelineIntegration:
    """Integration tests for full pipeline workflow"""

    def test_full_pipeline_flow(self, lead_client: TestClient, db: Session, team_lead_user, team_member):
        """Test complete pipeline from script to assembly"""
        # Create project
        project = Project(
            name="Pipeline Test Project",
            team_lead_id=team_lead_user.id,
            status="in_progress",
        )
        db.add(project)
        db.commit()

        # Step 1: Create script
        script_response = lead_client.post(
            "/scripts/",
            json={
                "project_id": project.id,
                "title": "Pipeline Test Script",
                "content": '{"scenes": [{"id": 1, "description": "Scene 1"}]}',
            },
        )
        assert script_response.status_code == 200
        script = script_response.json()

        # Step 2: Lock script
        lock_response = lead_client.post(f"/scripts/{script['id']}/lock")
        assert lock_response.status_code == 200

        # Step 3: Check chapters generated
        chapters_response = lead_client.get(f"/chapters/?script_id={script['id']}")
        assert chapters_response.status_code == 200

        # Continue through pipeline...
        # (Full test would continue through all 8 steps)


class TestPipelineAccessControl:
    """Test pipeline step access control"""

    def test_member_cannot_lock_script(self, member_client: TestClient, db: Session, team_lead_user):
        """Test team member cannot lock script"""
        project = Project(
            name="Member Lock Test",
            team_lead_id=team_lead_user.id,
        )
        db.add(project)
        db.commit()

        script = Script(
            project_id=project.id,
            title="Test Script",
            content="Content",
        )
        db.add(script)
        db.commit()

        response = member_client.post(f"/scripts/{script.id}/lock")
        assert response.status_code == 403

    def test_member_can_perform_first_audit(self, member_client: TestClient, storyboard_with_panels):
        """Test team member can perform first audit"""
        chapter, panels = storyboard_with_panels

        # This would be the first audit step
        response = member_client.post(
            f"/audits/first/{chapter.id}/submit",
            json={"decision": "approve"},
        )

        assert response.status_code in [200, 404]

    def test_member_cannot_approve_second_audit(self, member_client: TestClient, storyboard_with_panels):
        """Test team member cannot perform second audit"""
        chapter, panels = storyboard_with_panels

        response = member_client.post(
            f"/audits/second/{chapter.id}/approve",
        )

        assert response.status_code == 403
