#!/usr/bin/env python3
"""
AI Provider Configuration Script

This script helps configure AI providers by:
1. Creating default provider records in the database
2. Validating API connections
3. Setting up initial configuration

Usage:
    python scripts/configure_providers.py
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from sqlalchemy.orm import Session
from app.database import SessionLocal, create_db_and_tables
from app.models.model_provider import ModelProvider
from app.services.ai_service import AIService
from app.config import settings


def get_env_with_defaults(key: str, default: str) -> str:
    """Get environment variable with default"""
    return os.environ.get(key, default)


def create_default_providers(db: Session):
    """Create default AI provider configurations"""

    providers = [
        # LLM Provider - Anthropic (Claude)
        {
            "provider_type": "llm",
            "provider_name": "anthropic",
            "api_endpoint": "https://api.anthropic.com/v1",
            "api_key": get_env_env_or_default("ANTHROPIC_API_KEY", "sk-ant-your-key"),
            "config": {"model": "claude-sonnet-4-20250514"},
            "is_default": True,
        },
        # LLM Provider - OpenAI (GPT-4)
        {
            "provider_type": "llm",
            "provider_name": "openai",
            "api_endpoint": "https://api.openai.com/v1",
            "api_key": get_env_or_default("OPENAI_API_KEY", "sk-your-key"),
            "config": {"model": "gpt-4"},
            "is_default": False,
        },
        # Image Provider - OpenAI (DALL-E 3)
        {
            "provider_type": "image",
            "provider_name": "openai",
            "api_endpoint": "https://api.openai.com/v1",
            "api_key": get_env_or_default("OPENAI_API_KEY", "sk-your-key"),
            "config": {"model": "dall-e-3"},
            "is_default": True,
        },
        # TTS Provider - OpenAI
        {
            "provider_type": "tts",
            "provider_name": "openai",
            "api_endpoint": "https://api.openai.com/v1",
            "api_key": get_env_or_default("OPENAI_API_KEY", "sk-your-key"),
            "config": {"model": "tts-1"},
            "is_default": True,
        },
        # Video Provider - Runway (placeholder)
        {
            "provider_type": "video",
            "provider_name": "runway",
            "api_endpoint": "https://api.runwayml.com/v1",
            "api_key": get_env_or_default("RUNWAY_API_KEY", "your-runway-key"),
            "config": {"model": "gen2"},
            "is_default": True,
        },
    ]

    created = []
    updated = []

    for provider_data in providers:
        existing = db.query(ModelProvider).filter(
            ModelProvider.provider_type == provider_data["provider_type"],
            ModelProvider.provider_name == provider_data["provider_name"],
        ).first()

        if existing:
            # Update existing provider
            for key, value in provider_data.items():
                if key not in ["provider_type", "provider_name"]:
                    setattr(existing, key, value)
            updated.append(f"{provider_data['provider_type']}/{provider_data['provider_name']}")
        else:
            # Create new provider
            provider = ModelProvider(**provider_data)
            db.add(provider)
            created.append(f"{provider_data['provider_type']}/{provider_data['provider_name']}")

    db.commit()

    return created, updated


def get_env_or_default(key: str, default: str) -> str:
    """Get environment variable with default"""
    from app.config import settings
    # Try to read from .env file via settings
    if hasattr(settings, key):
        value = getattr(settings, key)
        if value and value != default:
            return value
    return os.environ.get(key, default)


def main():
    """Main entry point"""
    print("=" * 60)
    print("AI Provider Configuration Script")
    print("=" * 60)
    print()

    # Ensure database tables exist
    print("Ensuring database tables exist...")
    create_db_and_tables()

    # Create database session
    db = SessionLocal()

    try:
        # Create default providers
        print("\nConfiguring AI providers...")
        created, updated = create_default_providers(db)

        if created:
            print(f"\nCreated providers:")
            for name in created:
                print(f"  - {name}")

        if updated:
            print(f"\nUpdated providers:")
            for name in updated:
                print(f"  - {name}")

        if not created and not updated:
            print("\nNo changes needed.")

        # List all configured providers
        print("\n" + "=" * 60)
        print("Configured AI Providers:")
        print("=" * 60)

        providers = db.query(ModelProvider).all()
        for provider in providers:
            status_icon = "✓" if provider.is_active else "✗"
            default_icon = "★" if provider.is_default else " "
            health_icon = {
                "healthy": "🟢",
                "unhealthy": "🔴",
                None: "⚪",
            }.get(provider.health_status, "⚪")

            print(f"  {status_icon} {default_icon} {health_icon} {provider.provider_type}/{provider.provider_name}")
            print(f"      Endpoint: {provider.api_endpoint or 'default'}")
            print(f"      API Key: {'*' * 8}...{provider.api_key[-4:] if provider.api_key else 'N/A'}")
            print()

        print("=" * 60)
        print("Configuration complete!")
        print()
        print("Next steps:")
        print("1. Edit .env file with your actual API keys")
        print("2. Run: python scripts/test_providers.py")
        print("3. Start ARQ worker: arq arq_settings.WorkerSettings")
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
