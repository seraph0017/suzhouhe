"""
Pytest conftest.py - Shared fixtures for all tests

This module provides shared test fixtures including:
- Database session with transaction rollback
- Test users (admin, team_lead, team_member)
- Test projects
- Authentication tokens
- Mock AI services
"""

import pytest
import asyncio
from typing import Generator, AsyncGenerator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import redis

from app.main import app
from app.database import Base, get_db
from app.models.user import User, UserRole
from app.models.project import Project, ProjectMember, ProjectMemberRole
from app.models.script import Script, ScriptStatus
from app.models.chapter import Chapter, ChapterStatus
from app.models.storyboard import Storyboard, StoryboardStatus
from app.models.asset import Asset, AssetType, AssetStatus
from app.models.review import Review, ReviewType, ReviewStatus
from app.models.model_provider import ModelProvider
from app.utils.security import get_password_hash, create_access_token


# =============================================================================
# Database Configuration for Testing
# =============================================================================

# Use SQLite for simple unit tests (in-memory)
# For integration tests, use PostgreSQL test database
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
# SQLALCHEMY_DATABASE_URL = "postgresql://test:test@localhost:5432/manga_test"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override get_db dependency for testing"""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def db() -> Generator:
    """
    Create a fresh database for each test function.
    All tables are created before the test and dropped after.
    """
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db) -> Generator:
    """
    Create a test client with database override.
    """
    app.dependency_overrides[get_db] = lambda: db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


# =============================================================================
# Authentication Fixtures
# =============================================================================

@pytest.fixture
def admin_token(db) -> str:
    """Generate JWT token for admin user"""
    user = db.query(User).filter(User.email == "admin@test.com").first()
    if not user:
        user = _create_user(db, "admin@test.com", "TestPass123!", UserRole.ADMIN, "Admin User")
    return create_access_token(data={"sub": str(user.id)})


@pytest.fixture
def team_lead_token(db) -> str:
    """Generate JWT token for team lead user"""
    user = db.query(User).filter(User.email == "lead@test.com").first()
    if not user:
        user = _create_user(db, "lead@test.com", "TestPass123!", UserRole.TEAM_LEAD, "Team Lead")
    return create_access_token(data={"sub": str(user.id)})


@pytest.fixture
def team_member_token(db) -> str:
    """Generate JWT token for team member user"""
    user = db.query(User).filter(User.email == "member@test.com").first()
    if not user:
        user = _create_user(db, "member@test.com", "TestPass123!", UserRole.TEAM_MEMBER, "Team Member")
    return create_access_token(data={"sub": str(user.id)})


@pytest.fixture
def inactive_user_token(db) -> str:
    """Generate JWT token for inactive user"""
    user = db.query(User).filter(User.email == "inactive@test.com").first()
    if not user:
        user = _create_user(db, "inactive@test.com", "TestPass123!", UserRole.TEAM_MEMBER, "Inactive User", is_active=False)
    return create_access_token(data={"sub": str(user.id)})


def _create_user(db, email: str, password: str, role: UserRole, name: str, is_active: bool = True) -> User:
    """Helper to create a test user"""
    user = User(
        email=email,
        name=name,
        password_hash=get_password_hash(password),
        role=role,
        is_active=is_active,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# =============================================================================
# User Fixtures
# =============================================================================

@pytest.fixture
def admin_user(db) -> User:
    """Create and return admin user"""
    return _create_user(db, "admin@test.com", "TestPass123!", UserRole.ADMIN, "Admin User")


@pytest.fixture
def team_lead_user(db) -> User:
    """Create and return team lead user"""
    return _create_user(db, "lead@test.com", "TestPass123!", UserRole.TEAM_LEAD, "Team Lead")


@pytest.fixture
def team_member(db) -> User:
    """Create and return team member user"""
    return _create_user(db, "member@test.com", "TestPass123!", UserRole.TEAM_MEMBER, "Team Member")


@pytest.fixture
def inactive_user(db) -> User:
    """Create and return inactive user"""
    return _create_user(db, "inactive@test.com", "TestPass123!", UserRole.TEAM_MEMBER, "Inactive User", is_active=False)


# =============================================================================
# Project Fixtures
# =============================================================================

@pytest.fixture
def test_project(db, team_lead_user) -> Project:
    """Create and return a test project"""
    project = Project(
        name="Test Manga A",
        description="Test project for manga production",
        team_lead_id=team_lead_user.id,
        status="planning",
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@pytest.fixture
def test_project_in_progress(db, team_lead_user) -> Project:
    """Create and return a test project in progress"""
    project = Project(
        name="Test Manga B",
        description="Test project in progress",
        team_lead_id=team_lead_user.id,
        status="in_progress",
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@pytest.fixture
def archived_project(db, team_lead_user) -> Project:
    """Create and return an archived project"""
    project = Project(
        name="Archived Project",
        description="Test archived project",
        team_lead_id=team_lead_user.id,
        status="archived",
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@pytest.fixture
def project_with_member(db, team_lead_user, team_member) -> Project:
    """Create a project with a team member assigned"""
    project = Project(
        name="Team Project",
        description="Project with team members",
        team_lead_id=team_lead_user.id,
        status="in_progress",
    )
    db.add(project)
    db.commit()
    db.refresh(project)

    # Add team member
    membership = ProjectMember(
        project_id=project.id,
        user_id=team_member.id,
        role=ProjectMemberRole.MEMBER,
    )
    db.add(membership)
    db.commit()
    db.refresh(project)
    return project


# =============================================================================
# Pipeline Fixtures
# =============================================================================

@pytest.fixture
def script_with_chapters(db, test_project) -> tuple:
    """Create a script with chapters for pipeline testing"""
    # Create script
    script = Script(
        project_id=test_project.id,
        title="Test Script",
        content='{"scenes": [{"id": 1, "description": "Opening scene", "dialogue": "Hello!"}]}',
        version=1,
        status=ScriptStatus.LOCKED,
        is_locked=True,
    )
    db.add(script)
    db.commit()
    db.refresh(script)

    # Create chapters
    chapters = []
    for i in range(3):
        chapter = Chapter(
            script_id=script.id,
            order=i + 1,
            title=f"Chapter {i + 1}",
            content=f"Content for chapter {i + 1}",
            summary=f"Summary for chapter {i + 1}",
            status=ChapterStatus.DRAFT,
        )
        db.add(chapter)
        chapters.append(chapter)

    db.commit()
    for ch in chapters:
        db.refresh(ch)

    return script, chapters


@pytest.fixture
def storyboard_with_panels(db, script_with_chapters) -> tuple:
    """Create storyboard panels for a chapter"""
    script, chapters = script_with_chapters
    chapter = chapters[0]

    panels = []
    for i in range(5):
        panel = Storyboard(
            chapter_id=chapter.id,
            order=i + 1,
            title=f"Panel {i + 1}",
            visual_description=f"Visual description for panel {i + 1}",
            camera_direction="CLOSE_UP",
            dialogue=f"Dialogue line {i + 1}",
            duration_seconds=3.0,
            emotion="neutral",
        )
        db.add(panel)
        panels.append(panel)

    db.commit()
    for p in panels:
        db.refresh(p)

    return chapter, panels


@pytest.fixture
def assets_for_panels(db, storyboard_with_panels) -> tuple:
    """Create generated assets for storyboard panels"""
    chapter, panels = storyboard_with_panels

    all_assets = []
    for panel in panels:
        # Create 3 image options per panel
        for j in range(3):
            image = Asset(
                project_id=chapter.project_id,
                storyboard_id=panel.id,
                type=AssetType.IMAGE,
                file_name=f"panel_{panel.id}_opt_{j}.png",
                file_path=f"/images/panel_{panel.id}_opt_{j}.png",
                url=f"https://test.storage/images/panel_{panel.id}_opt_{j}.png",
                mime_type="image/png",
                metadata={"generation_params": {"seed": j}, "is_selected": j == 0},
                status=AssetStatus.COMPLETED,
            )
            db.add(image)
            all_assets.append(image)

        # Create audio per panel
        audio = Asset(
            project_id=chapter.project_id,
            storyboard_id=panel.id,
            type=AssetType.AUDIO,
            file_name=f"panel_{panel.id}.wav",
            file_path=f"/audio/panel_{panel.id}.wav",
            url=f"https://test.storage/audio/panel_{panel.id}.wav",
            mime_type="audio/wav",
            metadata={"duration_sec": 3.0, "voice_id": "zh-CN-XiaoxiaoNeural"},
            status=AssetStatus.COMPLETED,
            duration_seconds=3.0,
        )
        db.add(audio)
        all_assets.append(audio)

    db.commit()
    return chapter, panels, all_assets


# =============================================================================
# Review/Audit Fixtures
# =============================================================================

@pytest.fixture
def first_audit_review(db, team_member, storyboard_with_panels) -> Review:
    """Create a first audit review"""
    chapter, _ = storyboard_with_panels
    review = Review(
        review_type=ReviewType.FIRST_AUDIT,
        target_type="chapter",
        target_id=chapter.id,
        reviewer_id=team_member.id,
        status=ReviewStatus.PENDING,
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


@pytest.fixture
def second_audit_review(db, team_lead_user, assets_for_panels) -> Review:
    """Create a second audit review"""
    chapter, _, _ = assets_for_panels
    review = Review(
        review_type=ReviewType.SECOND_AUDIT,
        target_type="chapter_video",
        target_id=chapter.id,
        reviewer_id=team_lead_user.id,
        status=ReviewStatus.PENDING,
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


# =============================================================================
# Model Provider Fixtures
# =============================================================================

@pytest.fixture
def llm_provider(db) -> ModelProvider:
    """Create an LLM provider configuration"""
    provider = ModelProvider(
        provider_type="llm",
        name="openai",
        display_name="OpenAI GPT-4",
        api_endpoint="https://api.openai.com/v1",
        api_key="encrypted_test_key_llm",
        config={"model": "gpt-4", "max_tokens": 4096},
        is_active=True,
        is_default=True,
    )
    db.add(provider)
    db.commit()
    db.refresh(provider)
    return provider


@pytest.fixture
def image_provider(db) -> ModelProvider:
    """Create an Image generation provider configuration"""
    provider = ModelProvider(
        provider_type="image",
        name="stability_ai",
        display_name="Stability AI SDXL",
        api_endpoint="https://api.stability.ai/v1",
        api_key="encrypted_test_key_image",
        config={"model": "sdxl", "style": "anime"},
        is_active=True,
        is_default=True,
    )
    db.add(provider)
    db.commit()
    db.refresh(provider)
    return provider


@pytest.fixture
def tts_provider(db) -> ModelProvider:
    """Create a TTS provider configuration"""
    provider = ModelProvider(
        provider_type="tts",
        name="azure_tts",
        display_name="Azure Text-to-Speech",
        api_endpoint="https://eastus.api.cognitive.microsoft.com/cognitiveservices/v1",
        api_key="encrypted_test_key_tts",
        config={"voices": ["zh-CN-XiaoxiaoNeural", "zh-CN-YunxiNeural"]},
        is_active=True,
        is_default=True,
    )
    db.add(provider)
    db.commit()
    db.refresh(provider)
    return provider


@pytest.fixture
def video_provider(db) -> ModelProvider:
    """Create a Video generation provider configuration"""
    provider = ModelProvider(
        provider_type="video",
        name="heygen",
        display_name="HeyGen Lip-Sync",
        api_endpoint="https://api.heygen.com/v1",
        api_key="encrypted_test_key_video",
        config={"fps": 30, "resolution": "1920x1080"},
        is_active=True,
        is_default=True,
    )
    db.add(provider)
    db.commit()
    db.refresh(provider)
    return provider


# =============================================================================
# HTTP Client Fixtures with Authentication
# =============================================================================

@pytest.fixture
def auth_client(client, admin_token) -> TestClient:
    """Test client with admin authentication"""
    client.headers["Authorization"] = f"Bearer {admin_token}"
    return client


@pytest.fixture
def lead_client(client, team_lead_token) -> TestClient:
    """Test client with team lead authentication"""
    client.headers["Authorization"] = f"Bearer {team_lead_token}"
    return client


@pytest.fixture
def member_client(client, team_member_token) -> TestClient:
    """Test client with team member authentication"""
    client.headers["Authorization"] = f"Bearer {team_member_token}"
    return client


# =============================================================================
# Mock Services Fixtures
# =============================================================================

@pytest.fixture
def mock_llm_response():
    """Mock LLM API response"""
    return {
        "script": {
            "title": "Generated Script",
            "scenes": [
                {"id": 1, "description": "Scene 1 description", "dialogue": "Hello!"},
                {"id": 2, "description": "Scene 2 description", "dialogue": "How are you?"},
            ]
        }
    }


@pytest.fixture
def mock_image_generation_response():
    """Mock Image generation API response"""
    return {
        "images": [
            {"id": "img_1", "url": "https://test.storage/gen1.png"},
            {"id": "img_2", "url": "https://test.storage/gen2.png"},
            {"id": "img_3", "url": "https://test.storage/gen3.png"},
        ]
    }


@pytest.fixture
def mock_tts_generation_response():
    """Mock TTS generation API response"""
    return {
        "audio": {
            "id": "audio_1",
            "url": "https://test.storage/audio.wav",
            "duration_sec": 3.5,
        }
    }


@pytest.fixture
def mock_video_generation_response():
    """Mock Video generation API response"""
    return {
        "video": {
            "id": "video_1",
            "url": "https://test.storage/video.mp4",
            "duration_sec": 3.5,
            "resolution": "1920x1080",
        }
    }


# =============================================================================
# Redis Fixtures (for task queue testing)
# =============================================================================

@pytest.fixture
def redis_client():
    """Create a Redis client for task queue testing"""
    try:
        client = redis.Redis(host='localhost', port=6379, db=1)
        client.ping()
        yield client
        client.flushdb()
    except redis.ConnectionError:
        pytest.skip("Redis not available")


# =============================================================================
# Test Helper Functions
# =============================================================================

def create_authenticated_client(token: str) -> TestClient:
    """Helper to create an authenticated test client"""
    from fastapi.testclient import TestClient
    from app.main import app
    from app.database import get_db

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    client.headers["Authorization"] = f"Bearer {token}"
    return client


def assert_response_ok(response, expected_keys: list = None):
    """Helper to assert response is OK and contains expected keys"""
    assert response.status_code == 200
    if expected_keys:
        data = response.json()
        for key in expected_keys:
            assert key in data, f"Missing key: {key}"


def assert_response_error(response, expected_status: int = 400):
    """Helper to assert response is an error"""
    assert response.status_code == expected_status
    data = response.json()
    assert "detail" in data
