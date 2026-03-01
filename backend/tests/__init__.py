"""
AI Manga/Video Production Pipeline System - Test Suite

This package contains all tests for the backend API.

Test Files:
- test_auth.py: Authentication and authorization tests
- test_projects.py: Project management tests
- test_pipeline.py: 8-step pipeline workflow tests
- test_audit.py: Dual-audit system tests
- test_models.py: Model configuration tests
- test_dashboard.py: Dashboard and reports tests
- test_edge_cases.py: Edge cases and error scenarios
- conftest.py: Shared fixtures and helpers

Run tests:
    pytest                          # Run all tests
    pytest -v                       # Run with verbose output
    pytest -x                       # Stop on first failure
    pytest --cov=app               # Run with coverage report
    pytest tests/test_auth.py      # Run specific test file
    pytest -k "login"              # Run tests matching keyword

Test Categories:
- P0 (Critical): Run on every commit
- P1 (Important): Run nightly
- P2 (Edge cases): Run weekly/before releases
"""

__version__ = "1.0.0"
