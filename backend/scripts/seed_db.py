"""
Database Seeding Script

Initializes the database with:
1. Default admin user
2. Default AI provider configurations
3. Sample data for testing

Usage:
    python scripts/seed_db.py
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from sqlalchemy.orm import Session
from app.database import SessionLocal, create_db_and_tables
from app.models.user import User, UserRole
from app.models.model_provider import ModelProvider
from app.utils.security import get_password_hash


def create_admin_user(db: Session):
    """Create default admin user"""
    admin = db.query(User).filter(User.email == "admin@example.com").first()
    if admin:
        print("  Admin user already exists")
        return admin

    admin = User(
        email="admin@example.com",
        name="Admin",
        role=UserRole.ADMIN,
        password_hash=get_password_hash("admin123"),
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    print("  Created admin user: admin@example.com / admin123")
    return admin


def create_team_lead_user(db: Session):
    """Create default team lead user"""
    lead = db.query(User).filter(User.email == "lead@example.com").first()
    if lead:
        print("  Team lead user already exists")
        return lead

    lead = User(
        email="lead@example.com",
        name="Team Lead",
        role=UserRole.TEAM_LEAD,
        password_hash=get_password_hash("lead123"),
    )
    db.add(lead)
    db.commit()
    db.refresh(lead)
    print("  Created team lead user: lead@example.com / lead123")
    return lead


def create_team_member_user(db: Session):
    """Create default team member user"""
    member = db.query(User).filter(User.email == "member@example.com").first()
    if member:
        print("  Team member user already exists")
        return member

    member = User(
        email="member@example.com",
        name="Team Member",
        role=UserRole.TEAM_MEMBER,
        password_hash=get_password_hash("member123"),
    )
    db.add(member)
    db.commit()
    db.refresh(member)
    print("  Created team member user: member@example.com / member123")
    return member


def create_default_providers(db: Session):
    """Create default AI provider configurations"""
    providers_data = [
        # LLM Provider - Anthropic (Claude)
        {
            "provider_type": "llm",
            "name": "anthropic",
            "api_endpoint": "https://api.anthropic.com/v1",
            "api_key": os.environ.get("ANTHROPIC_API_KEY", ""),
            "config": {"model": "claude-sonnet-4-20250514"},
            "is_default": True,
        },
        # LLM Provider - OpenAI (GPT-4)
        {
            "provider_type": "llm",
            "name": "openai",
            "api_endpoint": "https://api.openai.com/v1",
            "api_key": os.environ.get("OPENAI_API_KEY", ""),
            "config": {"model": "gpt-4"},
            "is_default": False,
        },
        # Image Provider - OpenAI (DALL-E 3)
        {
            "provider_type": "image",
            "name": "openai",
            "api_endpoint": "https://api.openai.com/v1",
            "api_key": os.environ.get("OPENAI_API_KEY", ""),
            "config": {"model": "dall-e-3"},
            "is_default": True,
        },
        # TTS Provider - OpenAI
        {
            "provider_type": "tts",
            "name": "openai",
            "api_endpoint": "https://api.openai.com/v1",
            "api_key": os.environ.get("OPENAI_API_KEY", ""),
            "config": {"model": "tts-1"},
            "is_default": True,
        },
        # Video Provider - Runway
        {
            "provider_type": "video",
            "name": "runway",
            "api_endpoint": "https://api.runwayml.com/v1",
            "api_key": os.environ.get("RUNWAY_API_KEY", ""),
            "config": {"model": "gen2"},
            "is_default": True,
        },
    ]

    created_count = 0
    updated_count = 0

    for provider_data in providers_data:
        existing = db.query(ModelProvider).filter(
            ModelProvider.provider_type == provider_data["provider_type"],
            ModelProvider.name == provider_data["name"],
        ).first()

        if existing:
            # Update existing provider
            for key, value in provider_data.items():
                if key not in ["provider_type", "name"]:
                    setattr(existing, key, value)
            updated_count += 1
        else:
            # Create new provider
            provider = ModelProvider(**provider_data)
            db.add(provider)
            created_count += 1

    db.commit()
    print(f"  Created {created_count} providers, updated {updated_count} providers")


def main():
    """Main entry point"""
    print("=" * 60)
    print("Database Seeding Script")
    print("=" * 60)
    print()

    # Ensure database tables exist
    print("Creating database tables...")
    create_db_and_tables()

    # Create database session
    db = SessionLocal()

    try:
        print("\nCreating default users...")
        create_admin_user(db)
        create_team_lead_user(db)
        create_team_member_user(db)

        print("\nCreating default AI providers...")
        create_default_providers(db)

        print("\n" + "=" * 60)
        print("Database seeding completed!")
        print("=" * 60)
        print()
        print("Default users:")
        print("  Admin:       admin@example.com / admin123")
        print("  Team Lead:   lead@example.com / lead123")
        print("  Team Member: member@example.com / member123")
        print()
        print("Next steps:")
        print("  1. Set API keys in .env file")
        print("  2. Run: python scripts/configure_providers.py")
        print("  3. Start backend: uvicorn app.main:app --reload")
        print("  4. Start ARQ worker: arq arq_settings.WorkerSettings")
        print("=" * 60)

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        db.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
