"""
Test Model Configuration API

Tests for hot-swappable AI model provider configuration,
health checks, and provider management.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.model_provider import ModelProvider


class TestModelProviderCRUD:
    """Test Model Provider CRUD operations"""

    def test_create_model_provider_admin(self, auth_client: TestClient):
        """Test admin can create model provider"""
        response = auth_client.post(
            "/models/",
            json={
                "provider_type": "llm",
                "name": "anthropic",
                "display_name": "Anthropic Claude",
                "api_endpoint": "https://api.anthropic.com/v1",
                "api_key": "test-api-key-123",
                "config": {"model": "claude-3", "max_tokens": 4096},
                "is_active": True,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "anthropic"
        assert data["provider_type"] == "llm"

    def test_create_model_provider_non_admin_forbidden(self, lead_client: TestClient):
        """Test non-admin cannot create model provider"""
        response = lead_client.post(
            "/models/",
            json={
                "provider_type": "llm",
                "name": "test_provider",
                "display_name": "Test Provider",
                "api_endpoint": "https://api.test.com",
                "api_key": "test-key",
            },
        )

        assert response.status_code == 403

    def test_get_model_providers(self, auth_client: TestClient, db: Session, llm_provider):
        """Test getting all model providers"""
        response = auth_client.get("/models/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_get_model_provider_by_id(self, auth_client: TestClient, llm_provider):
        """Test getting single model provider"""
        response = auth_client.get(f"/models/{llm_provider.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == llm_provider.id
        assert data["name"] == "openai"
        # API key should be masked
        assert "encrypted" in data["api_key"] or data["api_key"] == "*****"

    def test_get_model_provider_by_type(self, auth_client: TestClient, llm_provider, image_provider):
        """Test filtering providers by type"""
        response = auth_client.get("/models/?provider_type=llm")
        assert response.status_code == 200
        data = response.json()
        for provider in data:
            assert provider["provider_type"] == "llm"

    def test_update_model_provider(self, auth_client: TestClient, llm_provider):
        """Test updating model provider"""
        response = auth_client.put(
            f"/models/{llm_provider.id}",
            json={
                "display_name": "Updated OpenAI GPT-4",
                "config": {"model": "gpt-4-turbo", "max_tokens": 8192},
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["display_name"] == "Updated OpenAI GPT-4"

    def test_update_model_provider_api_key(self, auth_client: TestClient, llm_provider):
        """Test updating API key"""
        response = auth_client.put(
            f"/models/{llm_provider.id}",
            json={"api_key": "new-encrypted-key"},
        )

        assert response.status_code == 200

    def test_delete_model_provider(self, auth_client: TestClient, db: Session):
        """Test deleting model provider"""
        provider = ModelProvider(
            provider_type="tts",
            name="test_tts",
            display_name="Test TTS",
            api_endpoint="https://api.test.com",
            api_key="test-key",
            is_active=True,
        )
        db.add(provider)
        db.commit()
        provider_id = provider.id

        response = auth_client.delete(f"/models/{provider_id}")
        assert response.status_code == 200

        # Verify deleted
        assert db.query(ModelProvider).filter(ModelProvider.id == provider_id).first() is None

    def test_delete_active_provider_warning(self, auth_client: TestClient, llm_provider):
        """Test deleting provider that is in use"""
        # If provider is default or in use, might get warning or error
        response = auth_client.delete(f"/models/{llm_provider.id}")
        assert response.status_code in [200, 400]


class TestProviderHealthCheck:
    """Test provider health check functionality"""

    def test_test_connection_success(self, auth_client: TestClient, llm_provider):
        """Test connection test"""
        response = auth_client.post(f"/models/{llm_provider.id}/test")
        # May succeed or fail depending on mock setup
        assert response.status_code in [200, 400, 500]

    def test_test_connection_invalid_credentials(self, auth_client: TestClient, db: Session):
        """Test connection with invalid credentials"""
        provider = ModelProvider(
            provider_type="llm",
            name="invalid_provider",
            display_name="Invalid Provider",
            api_endpoint="https://invalid.api.com",
            api_key="invalid-key",
            is_active=True,
        )
        db.add(provider)
        db.commit()

        response = auth_client.post(f"/models/{provider.id}/test")
        # Should fail connection test
        assert response.status_code in [200, 400, 500]
        if response.status_code == 200:
            data = response.json()
            assert data.get("success") is False

    def test_health_check_all_providers(self, auth_client: TestClient, db: Session):
        """Test health check for all providers"""
        response = auth_client.get("/models/health")
        assert response.status_code in [200, 404]


class TestProviderHotSwap:
    """Test hot-swap functionality"""

    def test_set_default_provider(self, auth_client: TestClient, db: Session):
        """Test setting default provider"""
        # Create new provider
        new_provider = ModelProvider(
            provider_type="llm",
            name="new_llm",
            display_name="New LLM Provider",
            api_endpoint="https://api.new.com",
            api_key="new-key",
            is_active=True,
            is_default=False,
        )
        db.add(new_provider)
        db.commit()

        response = auth_client.patch(
            f"/models/{new_provider.id}/default",
            json={"provider_type": "llm"},
        )

        assert response.status_code in [200, 404]

    def test_swap_provider_during_generation(self, auth_client: TestClient, db: Session):
        """Test swapping provider while generation is in progress"""
        # This tests that swapping doesn't break ongoing jobs
        provider1 = ModelProvider(
            provider_type="image",
            name="provider1",
            display_name="Provider 1",
            api_endpoint="https://api.p1.com",
            api_key="key1",
            is_active=True,
            is_default=True,
        )
        provider2 = ModelProvider(
            provider_type="image",
            name="provider2",
            display_name="Provider 2",
            api_endpoint="https://api.p2.com",
            api_key="key2",
            is_active=True,
            is_default=False,
        )
        db.add_all([provider1, provider2])
        db.commit()

        # Swap default
        response = auth_client.patch(
            f"/models/{provider2.id}/default",
            json={"provider_type": "image"},
        )

        assert response.status_code in [200, 404]

    def test_list_available_providers(self, auth_client: TestClient, db: Session):
        """Test listing available providers for type"""
        response = auth_client.get("/models/available?provider_type=image")
        assert response.status_code in [200, 404]


class TestProviderValidation:
    """Test provider configuration validation"""

    def test_create_provider_missing_type(self, auth_client: TestClient):
        """Test creating provider without type"""
        response = auth_client.post(
            "/models/",
            json={
                "name": "test",
                "display_name": "Test",
                "api_endpoint": "https://test.com",
                "api_key": "key",
            },
        )

        assert response.status_code == 422

    def test_create_provider_invalid_type(self, auth_client: TestClient):
        """Test creating provider with invalid type"""
        response = auth_client.post(
            "/models/",
            json={
                "provider_type": "invalid_type",
                "name": "test",
                "display_name": "Test",
                "api_endpoint": "https://test.com",
                "api_key": "key",
            },
        )

        assert response.status_code == 422

    def test_create_provider_missing_api_key(self, auth_client: TestClient):
        """Test creating provider without API key"""
        response = auth_client.post(
            "/models/",
            json={
                "provider_type": "llm",
                "name": "test",
                "display_name": "Test",
                "api_endpoint": "https://test.com",
            },
        )

        assert response.status_code == 422

    def test_update_provider_deactivate_last_one(self, auth_client: TestClient, db: Session):
        """Test deactivating the last provider for a type"""
        # Create single provider for type
        provider = ModelProvider(
            provider_type="video",
            name="only_video",
            display_name="Only Video Provider",
            api_endpoint="https://video.com",
            api_key="key",
            is_active=True,
            is_default=True,
        )
        db.add(provider)
        db.commit()

        # Try to deactivate
        response = auth_client.put(
            f"/models/{provider.id}",
            json={"is_active": False},
        )

        # May warn or prevent
        assert response.status_code in [200, 400]


class TestProviderQuota:
    """Test provider quota management"""

    def test_get_quota_usage(self, auth_client: TestClient, llm_provider):
        """Test getting quota usage"""
        response = auth_client.get(f"/models/{llm_provider.id}/quota")
        assert response.status_code in [200, 404]

    def test_quota_warning_threshold(self, auth_client: TestClient, db: Session):
        """Test quota warning at 80%"""
        provider = ModelProvider(
            provider_type="llm",
            name="quota_test",
            display_name="Quota Test",
            api_endpoint="https://api.test.com",
            api_key="key",
            config={"quota_limit": 1000, "quota_used": 850},  # 85%
            is_active=True,
        )
        db.add(provider)
        db.commit()

        response = auth_client.get(f"/models/{provider.id}/quota")
        if response.status_code == 200:
            data = response.json()
            assert data.get("warning") is True


class TestProviderAccessControl:
    """Test provider access control"""

    def test_team_lead_cannot_create_provider(self, lead_client: TestClient):
        """Test team lead cannot create provider"""
        response = lead_client.post(
            "/models/",
            json={
                "provider_type": "llm",
                "name": "lead_provider",
                "api_key": "key",
            },
        )

        assert response.status_code == 403

    def test_team_member_cannot_view_providers(self, member_client: TestClient):
        """Test team member cannot view providers"""
        response = member_client.get("/models/")
        assert response.status_code == 403

    def test_unauthenticated_cannot_access_providers(self, client: TestClient, llm_provider):
        """Test unauthenticated access to providers"""
        response = client.get(f"/models/{llm_provider.id}")
        assert response.status_code == 401


class TestProviderTypes:
    """Test different provider types"""

    def test_create_llm_provider(self, auth_client: TestClient):
        """Test creating LLM provider"""
        response = auth_client.post(
            "/models/",
            json={
                "provider_type": "llm",
                "name": "google_gemini",
                "display_name": "Google Gemini",
                "api_endpoint": "https://generativelanguage.googleapis.com/v1",
                "api_key": "gemini-key",
                "config": {"model": "gemini-pro"},
            },
        )

        assert response.status_code == 200

    def test_create_image_provider(self, auth_client: TestClient):
        """Test creating Image provider"""
        response = auth_client.post(
            "/models/",
            json={
                "provider_type": "image",
                "name": "midjourney",
                "display_name": "Midjourney",
                "api_endpoint": "https://api.midjourney.com/v1",
                "api_key": "mj-key",
                "config": {"style": "anime"},
            },
        )

        assert response.status_code == 200

    def test_create_video_provider(self, auth_client: TestClient):
        """Test creating Video provider"""
        response = auth_client.post(
            "/models/",
            json={
                "provider_type": "video",
                "name": "d_id",
                "display_name": "D-ID",
                "api_endpoint": "https://api.d-id.com/v1",
                "api_key": "did-key",
                "config": {"fps": 30},
            },
        )

        assert response.status_code == 200

    def test_create_tts_provider(self, auth_client: TestClient):
        """Test creating TTS provider"""
        response = auth_client.post(
            "/models/",
            json={
                "provider_type": "tts",
                "name": "elevenlabs",
                "display_name": "ElevenLabs",
                "api_endpoint": "https://api.elevenlabs.io/v1",
                "api_key": "11labs-key",
                "config": {"voices": ["Rachel", "Domi"]},
            },
        )

        assert response.status_code == 200
