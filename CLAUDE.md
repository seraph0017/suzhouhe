# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI Manga/Video Production Pipeline System (企业级 AI 漫剧生成流水线系统) - An industrial production system for generating manga-style videos using AI models.

## Core Architecture

### Role-Based Access Control
- **Admin**: System configuration, user management, API key management
- **Team Lead (组长)**: Script definition, pipeline configuration, final review (2nd audit)
- **Team Member (组员)**: Task execution, first review (1st audit), content adjustments

### 8-Step Dual-Audit Pipeline

1. **Script Base** - LLM-generated or uploaded script
2. **Script Refinement** - Interactive adjustments, locks to trigger downstream
3. **Chapter Breakdown** - Auto-generate chapter structure from script
4. **Storyboard Creation** - Generate shot scripts with camera directions and dialogue
5. **Material Generation** (After 1st Audit) - Image generation + TTS voice synthesis
6. **Video Generation** - Lip-sync accurate video from images + audio
7. **Smart Composition** - Add subtitles, BGM (AI recommended or generated)
8. **Chapter Assembly** (Before 2nd Audit) - Compile shots into chapter videos

### Key Requirements
- Multi-project parallel execution with data isolation
- Full audit trail with version rollback support
- Hot-swappable model configuration (LLM, Image, Video, TTS APIs)
- Dashboard with role-specific views

## Project Structure

```
suzhou/
├── needs/          # Requirements documents
└── CLAUDE.md
```

## Current Status

Repository initialized with requirements document only. No codebase exists yet.

## Next Steps for Development

When building this system, consider:
- Frontend: Vue 3 + TypeScript for reactive UI
- Backend: Python/FastAPI or Node.js for AI pipeline orchestration
- Database: PostgreSQL for structured data, object storage for media assets
- AI Integration: Abstraction layer for swappable model providers
