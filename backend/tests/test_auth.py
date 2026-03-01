"""
Test Authentication API

Tests for login, logout, token refresh, and authentication flow.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import User, UserRole
from app.utils.security import get_password_hash


class TestLogin:
    """Test login functionality"""

    def test_login_success(self, client: TestClient, db: Session):
        """Test successful login with valid credentials"""
        # Create test user
        user = User(
            email="test@example.com",
            name="Test User",
            password_hash=get_password_hash("TestPass123!"),
            role=UserRole.TEAM_MEMBER,
            is_active=True,
        )
        db.add(user)
        db.commit()

        # Login
        response = client.post(
            "/auth/login",
            data={
                "username": "test@example.com",
                "password": "TestPass123!",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data

    def test_login_invalid_email(self, client: TestClient):
        """Test login with non-existent email"""
        response = client.post(
            "/auth/login",
            data={
                "username": "nonexistent@example.com",
                "password": "TestPass123!",
            },
        )

        assert response.status_code == 401
        data = response.json()
        assert data["detail"] == "Incorrect email or password"

    def test_login_invalid_password(self, client: TestClient, db: Session):
        """Test login with wrong password"""
        user = User(
            email="test@example.com",
            name="Test User",
            password_hash=get_password_hash("TestPass123!"),
            role=UserRole.TEAM_MEMBER,
            is_active=True,
        )
        db.add(user)
        db.commit()

        response = client.post(
            "/auth/login",
            data={
                "username": "test@example.com",
                "password": "WrongPassword",
            },
        )

        assert response.status_code == 401
        data = response.json()
        assert data["detail"] == "Incorrect email or password"

    def test_login_inactive_user(self, client: TestClient, db: Session, inactive_user):
        """Test login with inactive account"""
        response = client.post(
            "/auth/login",
            data={
                "username": "inactive@test.com",
                "password": "TestPass123!",
            },
        )

        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == "Inactive user"

    def test_login_missing_password(self, client: TestClient):
        """Test login with missing password"""
        response = client.post(
            "/auth/login",
            data={
                "username": "test@example.com",
                "password": "",
            },
        )

        assert response.status_code == 422

    def test_login_invalid_email_format(self, client: TestClient):
        """Test login with invalid email format"""
        response = client.post(
            "/auth/login",
            data={
                "username": "invalid-email",
                "password": "TestPass123!",
            },
        )

        assert response.status_code == 422


class TestLogout:
    """Test logout functionality"""

    def test_logout_success(self, client: TestClient, db: Session, team_member_token):
        """Test successful logout"""
        client.headers["Authorization"] = f"Bearer {team_member_token}"
        response = client.post("/auth/logout")

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Successfully logged out"

    def test_logout_without_token(self, client: TestClient):
        """Test logout without authentication token"""
        response = client.post("/auth/logout")

        assert response.status_code == 401

    def test_logout_with_invalid_token(self, client: TestClient):
        """Test logout with invalid token"""
        client.headers["Authorization"] = "Bearer invalid_token"
        response = client.post("/auth/logout")

        assert response.status_code == 401


class TestTokenRefresh:
    """Test token refresh functionality"""

    def test_refresh_token_success(self, client: TestClient, db: Session, team_member_token):
        """Test successful token refresh"""
        client.headers["Authorization"] = f"Bearer {team_member_token}"
        response = client.post("/auth/refresh")

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_refresh_token_without_token(self, client: TestClient):
        """Test token refresh without authentication"""
        response = client.post("/auth/refresh")

        assert response.status_code == 401

    def test_refresh_token_with_invalid_token(self, client: TestClient):
        """Test token refresh with invalid token"""
        client.headers["Authorization"] = "Bearer invalid_token"
        response = client.post("/auth/refresh")

        assert response.status_code == 401

    def test_refresh_token_rotation(self, client: TestClient, db: Session, team_member_token):
        """Test that refresh token rotates (new token each time)"""
        client.headers["Authorization"] = f"Bearer {team_member_token}"

        # First refresh
        response1 = client.post("/auth/refresh")
        assert response1.status_code == 200
        token1 = response1.json()["access_token"]

        # Second refresh
        response2 = client.post("/auth/refresh")
        assert response2.status_code == 200
        token2 = response2.json()["access_token"]

        # Tokens should be different (rotation)
        assert token1 != token2


class TestGetCurrentUser:
    """Test get current user endpoint"""

    def test_get_current_user_success(self, client: TestClient, team_member_token):
        """Test getting current user info"""
        client.headers["Authorization"] = f"Bearer {team_member_token}"
        response = client.get("/auth/me")

        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "email" in data
        assert "name" in data
        assert "role" in data
        assert data["email"] == "member@test.com"

    def test_get_current_user_without_token(self, client: TestClient):
        """Test getting current user without authentication"""
        response = client.get("/auth/me")

        assert response.status_code == 401

    def test_get_current_user_admin(self, client: TestClient, admin_token):
        """Test getting admin user info"""
        client.headers["Authorization"] = f"Bearer {admin_token}"
        response = client.get("/auth/me")

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "admin@test.com"
        assert data["role"] == "admin"

    def test_get_current_user_team_lead(self, client: TestClient, team_lead_token):
        """Test getting team lead user info"""
        client.headers["Authorization"] = f"Bearer {team_lead_token}"
        response = client.get("/auth/me")

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "lead@test.com"
        assert data["role"] == "team_lead"


class TestAuthenticationIntegration:
    """Integration tests for authentication flow"""

    def test_full_auth_flow(self, client: TestClient, db: Session):
        """Test complete authentication flow: login -> use token -> refresh -> logout"""
        # Create user
        user = User(
            email="flow@example.com",
            name="Flow User",
            password_hash=get_password_hash("TestPass123!"),
            role=UserRole.TEAM_MEMBER,
            is_active=True,
        )
        db.add(user)
        db.commit()

        # Login
        login_response = client.post(
            "/auth/login",
            data={
                "username": "flow@example.com",
                "password": "TestPass123!",
            },
        )
        assert login_response.status_code == 200
        tokens = login_response.json()
        access_token = tokens["access_token"]

        # Use token to get user info
        client.headers["Authorization"] = f"Bearer {access_token}"
        me_response = client.get("/auth/me")
        assert me_response.status_code == 200
        assert me_response.json()["email"] == "flow@example.com"

        # Refresh token
        refresh_response = client.post("/auth/refresh")
        assert refresh_response.status_code == 200
        new_tokens = refresh_response.json()

        # Use new token
        client.headers["Authorization"] = f"Bearer {new_tokens['access_token']}"
        me_response2 = client.get("/auth/me")
        assert me_response2.status_code == 200

        # Logout
        logout_response = client.post("/auth/logout")
        assert logout_response.status_code == 200

    def test_multiple_device_login(self, client: TestClient, db: Session):
        """Test multiple devices can login simultaneously"""
        # Create user
        user = User(
            email="multi@example.com",
            name="Multi User",
            password_hash=get_password_hash("TestPass123!"),
            role=UserRole.TEAM_MEMBER,
            is_active=True,
        )
        db.add(user)
        db.commit()

        # Login from device 1
        device1_response = client.post(
            "/auth/login",
            data={
                "username": "multi@example.com",
                "password": "TestPass123!",
            },
        )
        assert device1_response.status_code == 200

        # Login from device 2
        device2_response = client.post(
            "/auth/login",
            data={
                "username": "multi@example.com",
                "password": "TestPass123!",
            },
        )
        assert device2_response.status_code == 200

        # Both tokens should work
        tokens1 = device1_response.json()
        tokens2 = device2_response.json()

        # Tokens should be different (different sessions)
        assert tokens1["access_token"] != tokens2["access_token"]

        # Both should be able to access user info
        client.headers["Authorization"] = f"Bearer {tokens1['access_token']}"
        assert client.get("/auth/me").status_code == 200

        client.headers["Authorization"] = f"Bearer {tokens2['access_token']}"
        assert client.get("/auth/me").status_code == 200


class TestPasswordValidation:
    """Test password validation rules"""

    def test_password_too_short(self, client: TestClient, db: Session):
        """Test password below minimum length"""
        # Try to create user with short password via direct DB insertion
        # Note: API validation would catch this during user registration
        user = User(
            email="shortpwd@example.com",
            name="Test User",
            password_hash=get_password_hash("short"),  # Less than 6 chars
            role=UserRole.TEAM_MEMBER,
            is_active=True,
        )
        db.add(user)
        db.commit()

        # Login should still work (password already hashed)
        response = client.post(
            "/auth/login",
            data={
                "username": "shortpwd@example.com",
                "password": "short",
            },
        )

        # Login works but this is a data issue, not auth issue
        assert response.status_code == 200

    def test_password_special_characters(self, client: TestClient, db: Session):
        """Test password with special characters"""
        special_password = "Test@Pass#123!$%^&*()"
        user = User(
            email="special@example.com",
            name="Test User",
            password_hash=get_password_hash(special_password),
            role=UserRole.TEAM_MEMBER,
            is_active=True,
        )
        db.add(user)
        db.commit()

        response = client.post(
            "/auth/login",
            data={
                "username": "special@example.com",
                "password": special_password,
            },
        )

        assert response.status_code == 200

    def test_password_unicode(self, client: TestClient, db: Session):
        """Test password with unicode characters"""
        unicode_password = "Test 密码 🎉Ümläut"
        user = User(
            email="unicode@example.com",
            name="Test User",
            password_hash=get_password_hash(unicode_password),
            role=UserRole.TEAM_MEMBER,
            is_active=True,
        )
        db.add(user)
        db.commit()

        response = client.post(
            "/auth/login",
            data={
                "username": "unicode@example.com",
                "password": unicode_password,
            },
        )

        assert response.status_code == 200
