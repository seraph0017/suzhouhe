#!/usr/bin/env python3
"""
AI Provider Connection Test Script

Tests connections to all configured AI providers.

Usage:
    python scripts/test_providers.py
"""

import sys
import os
import asyncio

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.services.ai_service import AIService


async def test_providers():
    """Test all configured AI providers"""
    db = SessionLocal()
    ai_service = AIService(db)

    print("=" * 60)
    print("AI Provider Connection Test")
    print("=" * 60)
    print()

    # Test each provider type
    provider_types = ["llm", "image", "tts", "video", "bgm"]
    results = {}

    for provider_type in provider_types:
        print(f"Testing {provider_type} provider...")
        try:
            is_valid = await ai_service.validate_provider(provider_type)
            results[provider_type] = {
                "success": is_valid,
                "error": None if is_valid else "Validation failed",
            }
            status = "✓ Pass" if is_valid else "✗ Fail"
            print(f"  {status}")
        except Exception as e:
            results[provider_type] = {
                "success": False,
                "error": str(e),
            }
            print(f"  ✗ Fail: {e}")

    print()
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)

    passed = sum(1 for r in results.values() if r["success"])
    total = len(results)

    for provider_type, result in results.items():
        status = "✓" if result["success"] else "✗"
        print(f"  {status} {provider_type}: {'Pass' if result['success'] else result['error']}")

    print()
    print(f"Results: {passed}/{total} providers working")
    print("=" * 60)

    # Test specific features
    print()
    print("Testing specific features...")
    print()

    # Test LLM text generation
    print("1. Testing LLM text generation (short test)...")
    try:
        result = await ai_service.generate_text(
            prompt="Say 'Hello, this is a test.' in one sentence.",
            max_tokens=50,
        )
        if result.success:
            print(f"   ✓ LLM response: {result.data[:50]}...")
        else:
            print(f"   ✗ LLM failed: {result.error}")
    except Exception as e:
        print(f"   ✗ LLM error: {e}")

    # Test TTS voices list
    print()
    print("2. Testing TTS voices list...")
    try:
        voices = await ai_service.list_voices()
        if voices:
            print(f"   ✓ Available voices: {len(voices)}")
            for voice in voices[:3]:
                print(f"      - {voice.get('name', voice.get('id', 'Unknown'))}")
        else:
            print("   ✗ No voices returned")
    except Exception as e:
        print(f"   ✗ TTS error: {e}")

    # Test image generation (single image)
    print()
    print("3. Testing image generation (single image, may take time)...")
    try:
        result = await ai_service.generate_images(
            prompt="A simple test image",
            count=1,
            save_to_storage=False,  # Don't save for test
        )
        if result.success:
            print(f"   ✓ Image generation successful")
        else:
            print(f"   ✗ Image generation failed: {result.error}")
    except Exception as e:
        print(f"   ✗ Image error: {e}")

    print()
    print("=" * 60)
    print("All tests completed!")
    print("=" * 60)

    db.close()
    return passed == total


def main():
    """Main entry point"""
    try:
        success = asyncio.run(test_providers())
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        return 1
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
