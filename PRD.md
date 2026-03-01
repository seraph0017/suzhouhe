# Product Requirements Document (PRD)
# 企业级 AI 漫剧生成流水线系统
# Enterprise AI Manga/Video Production Pipeline System

**Version:** 1.0
**Date:** 2026-03-01
**Author:** Product Manager
**Status:** Draft for Review

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [User Personas](#2-user-personas)
3. [User Stories](#3-user-stories)
4. [Functional Requirements](#4-functional-requirements)
5. [Dual-Audit Workflow](#5-dual-audit-workflow)
6. [Dashboard Requirements](#6-dashboard-requirements)
7. [Non-Functional Requirements](#7-non-functional-requirements)
8. [API Requirements](#8-api-requirements)
9. [Data Model Overview](#9-data-model-overview)
10. [Acceptance Criteria](#10-acceptance-criteria)

---

## 1. Executive Summary

### 1.1 Project Overview

The **Enterprise AI Manga/Video Production Pipeline System** is an industrial-grade production platform designed to democratize manga-style video creation. The system enables professional screenwriters (Team Leads) to control content quality while allowing general team members (without professional background) to execute production tasks through a standardized, guided workflow.

### 1.2 Business Goals

| Goal | Description | Priority |
|------|-------------|----------|
| **Democratize Production** | Enable non-expert team members to produce professional-quality manga videos | P0 |
| **Quality Control** | Implement dual-audit system to ensure content meets professional standards | P0 |
| **Efficiency** | Reduce manga video production time by 70% compared to traditional methods | P1 |
| **Scalability** | Support multiple concurrent projects with complete data isolation | P1 |
| **Flexibility** | Enable hot-swapping of AI model providers without code changes | P2 |

### 1.3 Success Metrics

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Production Cycle Time | < 4 hours per chapter | Time from script lock to final approval |
| First-Pass Approval Rate | > 80% | Percentage of content passing first audit |
| User Satisfaction Score | > 4.5/5 | Quarterly team member surveys |
| System Uptime | > 99.5% | Infrastructure monitoring |
| Model API Success Rate | > 98% | API call monitoring |

### 1.4 Scope

**In Scope (Phase 1):**
- Complete 8-step pipeline workflow
- Role-based access control (Admin, Team Lead, Team Member)
- Dual-audit system (First audit by Team Member, Second audit by Team Lead)
- Role-specific dashboards
- Hot-swappable AI model configuration
- Multi-project support with data isolation
- Basic audit trail and version history

**Out of Scope (Phase 1):**
- Mobile application
- Real-time collaboration features
- Advanced analytics and reporting
- Third-party integrations beyond AI model APIs
- Automated subtitle generation (manual input supported)

---

## 2. User Personas

### 2.1 Administrator (管理员)

| Attribute | Description |
|-----------|-------------|
| **Name** | Chen Wei (陈伟) |
| **Role** | System Administrator |
| **Technical Proficiency** | High |
| **Goals** | Maintain system stability, manage users, configure resources |
| **Pain Points** | Manual API key rotation, lack of visibility into system health |
| **Key Needs** | User management dashboard, API configuration UI, audit logs |

**Scenario:** Chen needs to onboard a new team of 10 members to a new manga project. He creates the project, assigns the Team Lead, and configures the AI model API keys for the team.

---

### 2.2 Team Lead / 编剧组长 (Screenwriter Level)

| Attribute | Description |
|-----------|-------------|
| **Name** | Lin Xiaoyu (林小雨) |
| **Role** | Senior Screenwriter / Team Lead |
| **Technical Proficiency** | Medium-High |
| **Experience** | 5+ years in manga/script writing |
| **Goals** | Produce high-quality manga content, mentor team members |
| **Pain Points** | Inconsistent quality from junior members, time-consuming reviews |
| **Key Needs** | Script definition tools, pipeline configuration, final approval workflow |

**Scenario:** Lin defines the core script for a new manga series, configures the production pipeline settings, and reviews the final chapter videos before publication.

---

### 2.3 Team Member / 组员 (Production Staff)

| Attribute | Description |
|-----------|-------------|
| **Name** | Wang Fang (王芳) |
| **Role** | Production Team Member |
| **Technical Proficiency** | Low-Medium |
| **Experience** | No professional manga background |
| **Goals** | Complete assigned tasks efficiently, learn production skills |
| **Pain Points** | Unclear instructions, complex tools, fear of making mistakes |
| **Key Needs** | Guided task workflow, clear instructions, easy adjustment tools |

**Scenario:** Wang receives a task to execute the pipeline for Chapter 3. She follows the step-by-step wizard, selects images from generated options, and submits for first audit.

---

## 3. User Stories

### 3.1 Administrator Stories

| ID | User Story | Acceptance Criteria | Priority |
|----|-----------|---------------------|----------|
| A01 | As an Admin, I want to create and archive projects, so that I can organize production work | **Given** I am logged in as Admin<br>**When** I create a project with name, description, and team lead<br>**Then** the project is created and appears in the active projects list<br>**When** I archive a project<br>**Then** the project becomes read-only and moves to archived status<br>**When** I filter by status<br>**Then** I can view active and archived projects separately | P0 |
| A02 | As an Admin, I want to assign users to roles, so that proper access control is enforced | **Given** I am logged in as Admin<br>**When** I assign a role (Admin/Team Lead/Team Member) to a user<br>**Then** the role change takes effect immediately<br>**And** an audit log entry is created<br>**When** the user logs in<br>**Then** they see the dashboard appropriate for their new role | P0 |
| A03 | As an Admin, I want to configure AI model API keys, so that the system can call external services | **Given** I am logged in as Admin<br>**When** I add API credentials for a provider<br>**Then** the credentials are encrypted at rest<br>**When** I click "Test Connection"<br>**Then** the system validates the credentials and shows success/failure<br>**When** I save the configuration<br>**Then** the API key is stored encrypted (AES-256) | P0 |
| A04 | As an Admin, I want to view system health dashboard, so that I can monitor resource usage | **Given** I am logged in as Admin<br>**When** I view the system health dashboard<br>**Then** I see API quota usage, error rates, and active users<br>**When** any metric exceeds threshold<br>**Then** an alert is displayed prominently<br>**When** I click on audit logs<br>**Then** I can view filtered logs by date, user, and action | P1 |

### 3.2 Team Lead Stories

| ID | User Story | Acceptance Criteria | Priority |
|----|-----------|---------------------|----------|
| TL01 | As a Team Lead, I want to define the base script using LLM, so that I have a starting point for the manga | **Given** I am logged in as Team Lead<br>**When** I select an LLM model and provide a prompt<br>**Then** the system generates a structured script within 60 seconds<br>**When** the script is generated<br>**Then** it contains scenes, dialogue, and character definitions | P0 |
| TL02 | As a Team Lead, I want to upload an existing script, so that I can use pre-written content | **Given** I am logged in as Team Lead<br>**When** I upload a .txt or .docx file (max 10MB)<br>**Then** the script content is parsed and displayed in the editor<br>**When** the upload completes<br>**Then** a version history entry is created | P0 |
| TL03 | As a Team Lead, I want to interactively refine the script, so that it meets quality standards | **Given** I have a draft script<br>**When** I edit dialogue or scene descriptions<br>**Then** changes are saved with version tracking<br>**When** I view version history<br>**Then** I can compare versions side-by-side<br>**When** I lock the script<br>**Then** Chapter Breakdown is automatically triggered | P0 |
| TL04 | As a Team Lead, I want to configure the production pipeline, so that it matches project requirements | **Given** I am logged in as Team Lead<br>**When** I configure pipeline settings<br>**Then** I can define number of chapters and style guidelines<br>**When** I set model parameters<br>**Then** they apply to all generations in the project | P1 |
| TL05 | As a Team Lead, I want to review final chapter videos, so that only quality content is published | **Given** a chapter is submitted for second audit<br>**When** I view the chapter video<br>**Then** I can see metadata and audit history<br>**When** I approve<br>**Then** the chapter status changes to PUBLISHED<br>**When** I reject with comments<br>**Then** the chapter returns to the appropriate step with feedback | P0 |
| TL06 | As a Team Lead, I want to monitor team member workload, so that I can balance task distribution | **Given** I am logged in as Team Lead<br>**When** I view the team workload dashboard<br>**Then** I see task assignments per member with completion rates<br>**When** I reassign a task<br>**Then** the new assignee is notified and the task transfers immediately | P2 |

### 3.3 Team Member Stories

| ID | User Story | Acceptance Criteria | Priority |
|----|-----------|---------------------|----------|
| TM01 | As a Team Member, I want to see my assigned tasks, so that I know what to work on | **Given** I am logged in as Team Member<br>**When** I view my dashboard<br>**Then** I see tasks filtered by status (pending, in-progress, completed)<br>**When** a task has a due date<br>**Then** I see a visual indicator (color/icon) based on urgency<br>**When** I click on a pending task<br>**Then** I can start the task with one click | P0 |
| TM02 | As a Team Member, I want to execute chapter breakdown, so that the script is organized into chapters | **Given** a locked script<br>**When** I view chapter breakdown<br>**Then** I see auto-generated chapters with titles and summaries<br>**When** I adjust chapter boundaries<br>**Then** the changes are saved and chapter numbers update automatically | P0 |
| TM03 | As a Team Member, I want to review generated storyboards, so that they are ready for production | **Given** chapters are created<br>**When** I view storyboard panels<br>**Then** I see camera directions, dialogue, and image prompts<br>**When** I edit panel content<br>**Then** changes are saved<br>**When** I lock the storyboard<br>**Then** material generation is automatically triggered | P0 |
| TM04 | As a Team Member, I want to select images from generated options, so that each scene has the best visual | **Given** image generation is complete<br>**When** I view a panel<br>**Then** I see 3-5 generated image options<br>**When** I select an image<br>**Then** it is marked as selected and others are archived<br>**When** I click regenerate<br>**Then** new images are generated for that panel<br>**When** I preview slideshow<br>**Then** I see selected images in sequence | P0 |
| TM05 | As a Team Member, I want to review generated voice acting, so that audio matches the scene | **Given** TTS generation is complete<br>**When** I view a panel<br>**Then** I can play the generated audio<br>**When** I select a different voice actor<br>**Then** I can regenerate with the new voice<br>**When** I adjust parameters (speed, pitch, emotion)<br>**Then** new audio is generated with updated settings | P0 |
| TM06 | As a Team Member, I want to perform first audit, so that issues are caught before final review | **Given** all materials are generated<br>**When** I view the first audit interface<br>**Then** I see all assets in storyboard layout<br>**When** I mark panels as approved/rejected<br>**Then** my selections are saved<br>**When** I add comments<br>**Then** they are attached to specific panels<br>**When** I submit the audit<br>**Then** the chapter proceeds to second audit (if approved) | P0 |
| TM07 | As a Team Member, I want to configure BGM for chapters, so that the mood matches the scene | **Given** I am in smart composition step<br>**When** I browse BGM options<br>**Then** I see AI-recommended tracks based on chapter mood<br>**When** I preview BGM with video<br>**Then** I can adjust the volume balance<br>**When** I select a BGM track<br>**Then** it is applied to the chapter | P1 |

---

## 4. Functional Requirements

### 4.1 Pipeline Overview

The system implements an **8-Step Dual-Audit Pipeline** for manga video production:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        AI Manga Production Pipeline                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Step 1        Step 2        Step 3        Step 4                          │
│  ┌─────┐      ┌─────┐      ┌─────┐      ┌─────┐                           │
│  │Script│─────>│Refine│─────>│Chapter│─────>│Storyboard│                  │
│  │Base  │      │      │      │Break │      │Create    │                   │
│  └─────┘      └─────┘      └─────┘      └─────┘                           │
│     │            │            │            │                               │
│     ▼            ▼            ▼            ▼                               │
│  [LLM/Upload] [Lock Trigger] [Auto-Gen]   [Lock Trigger]                  │
│                                                                             │
│                          🔴 FIRST AUDIT (Team Member)                       │
│                                    ▼                                        │
│  Step 5        Step 6        Step 7        Step 8                          │
│  ┌─────┐      ┌─────┐      ┌─────┐      ┌─────┐                           │
│  │Material│<───│Video │<───│Smart │<───│Chapter│                          │
│  │Gen    │      │Gen   │      │Compose│    │Assemble│                    │
│  └─────┘      └─────┘      └─────┘      └─────┘                           │
│     │            │            │            │                               │
│     ▼            ▼            ▼            ▼                               │
│  [Image+TTS]  [Lip-Sync]   [BGM+Sub]    [Final]                           │
│                                                                             │
│                          🟠 SECOND AUDIT (Team Lead)                        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 4.2 Step 1: Script Base (剧本基座)

**Description:** Establish the foundational script for the manga production.

**Input:** Empty canvas or uploaded script draft

**Operations:**

| Option | Description | Configuration |
|--------|-------------|---------------|
| **LLM Generation** | Use configured LLM to generate script from prompt | - Select LLM model<br>- Provide outline/prompt<br>- Set tone/style parameters |
| **Direct Upload** | Upload existing script file | - Supported formats: .txt, .docx<br>- File size limit: 10MB<br>- Character encoding: UTF-8 |

**Output:** Standardized format script with:
- Scene descriptions
- Character dialogue
- Stage directions
- Estimated duration per scene

**Validation Rules:**
- Script must contain at least 1 scene
- Each scene must have description
- Dialogue must be attributed to characters
- Maximum script length: 50,000 characters

**UI Requirements:**
- Split view: Editor (left) + Preview (right)
- Scene navigator sidebar
- Character list panel
- Word/character count display

---

### 4.3 Step 2: Script Refinement (剧本精调)

**Description:** Interactive refinement of the base script before locking for downstream processing.

**Operations:**

| Action | Description | Trigger |
|--------|-------------|---------|
| **Edit Dialogue** | Modify character dialogue lines | Inline editing |
| **Adjust Scenes** | Modify scene descriptions, add/remove scenes | Scene editor |
| **Character Management** | Add, rename, or merge characters | Character panel |
| **Version Compare** | View differences between versions | Version history |
| **Lock Script** | Finalize script, trigger Chapter Breakdown | Lock button with confirmation |

**Output:** Locked version of script (triggers Step 3 auto-generation)

**Lock Constraints:**
- Script must pass validation (Section 4.2)
- All scenes must have dialogue or description
- Confirmation modal required for lock action
- Unlock requires Team Lead approval

**UI Requirements:**
- Track changes highlighting
- Comment/thread support per scene
- Lock status indicator (locked/unlocked)
- Version selector dropdown

---

### 4.4 Step 3: Chapter Breakdown (章节拆解)

**Description:** Automatically generate chapter structure from the locked script.

**Auto-Generation Logic:**

```python
# Pseudo-code for chapter breakdown algorithm
def generate_chapters(script):
    chapters = []
    current_chapter = Chapter()

    for scene in script.scenes:
        # Chapter break triggers:
        if (scene.is_major_transition      # Explicit scene break marker
            or current_chapter.duration > MAX_CHAPTER_DURATION  # ~10 minutes
            or scene.location_change       # New location
            or scene.time_jump             # Time skip indicator
        ):
            if current_chapter.scenes:
                chapters.append(current_chapter)
            current_chapter = Chapter()

        current_chapter.add_scene(scene)

    # Add remaining scenes
    if current_chapter.scenes:
        chapters.append(current_chapter)

    # Auto-generate chapter titles
    for chapter in chapters:
        chapter.title = LLM.generate_title(chapter.scenes)
        chapter.summary = LLM.generate_summary(chapter.scenes)

    return chapters
```

**Manual Adjustment Options:**

| Action | Description |
|--------|-------------|
| **Merge Chapters** | Combine two adjacent chapters |
| **Split Chapter** | Divide a chapter at selected scene |
| **Reorder Chapters** | Drag-and-drop chapter ordering |
| **Edit Metadata** | Modify chapter title, summary, estimated duration |

**Output:** Editable chapter list with:
- Chapter number and title
- Chapter summary
- Scene list per chapter
- Estimated duration

**Validation Rules:**
- Minimum 1 chapter required
- Maximum chapter duration: 15 minutes (estimated)
- All scenes must belong to exactly one chapter
- Chapter order must be sequential (1, 2, 3...)

**UI Requirements:**
- Chapter card view with expandable scene list
- Drag-and-drop reordering
- Visual indicator for estimated duration
- Split/merge action buttons

---

### 4.5 Step 4: Storyboard Creation (分镜创作)

**Description:** Generate detailed storyboard panels with camera directions and dialogue for each chapter.

**Auto-Generation Process:**

For each chapter, the system generates storyboard panels:

| Field | Generated From | Description |
|-------|----------------|-------------|
| **Panel Image Prompt** | Scene description + dialogue | Detailed prompt for image generation |
| **Camera Direction** | Scene emotion, action | Pan, zoom, close-up, wide shot |
| **Character Pose** | Dialogue context, action | Standing, sitting, emotional expression |
| **Background** | Scene location | Indoor, outdoor, specific setting |
| **Dialogue Text** | Script dialogue | Exact dialogue per panel |
| **Subtitle Text** | Dialogue | Formatted for display |

**Panel Data Structure:**

```json
{
  "panel_id": "uuid",
  "chapter_id": "uuid",
  "sequence_number": 1,
  "image_prompt": "Close-up of young woman, surprised expression, anime style...",
  "camera_direction": "ZOOM_IN",
  "character_pose": "STANDING_SURPRISED",
  "background": "MODERN_CLASSROOM_DAY",
  "dialogue": "你怎么会在这里？",
  "subtitle": "你怎么会在这里？",
  "estimated_duration_sec": 3.5,
  "voice_actor_id": null,
  "selected_image_id": null,
  "selected_audio_id": null
}
```

**Manual Adjustment Options:**

| Action | Description |
|--------|-------------|
| **Edit Panel** | Modify any generated field |
| **Add Panel** | Insert new panel between existing panels |
| **Delete Panel** | Remove panel (with confirmation) |
| **Reorder Panels** | Change panel sequence within chapter |
| **Batch Edit** | Apply changes to multiple panels |

**Lock Trigger:** Locking the storyboard triggers Step 5 (Material Generation)

**UI Requirements:**
- Storyboard grid view (thumbnail + metadata)
- Panel detail editor (modal or side panel)
- Preview mode: Sequential panel slideshow
- Lock status indicator

---

### 4.6 First Audit Node (第一次审核)

**Owner:** Team Member (组员)

**Audit Scope:** Generated images and voice acting (from Step 5)

**Presentation:** Waterfall flow / Storyboard layout

**Image Selection Mechanism (抽卡制 - Card Draw System):**

| Feature | Description |
|---------|-------------|
| **Multi-Option Generation** | Generate 3-5 images per storyboard panel |
| **Selection Interface** | Thumbnail grid with select/regenerate options |
| **Regeneration** | Request new batch for specific panel |
| **Batch Preview** | Slideshow of selected images in sequence |

**Audit Actions:**

| Action | Description | Next State |
|--------|-------------|------------|
| **Approve All** | Accept all current selections | Proceed to Step 6 |
| **Selective Replace** | Replace specific images/audio | Stay in Step 5 |
| **Regenerate All** | Request new batch for all panels | Stay in Step 5 |
| **Add Comments** | Note issues for Team Lead review | Stay in Step 5 |

**Audit Checklist:**
- [ ] All panels have selected images
- [ ] Image style is consistent across chapter
- [ ] Character appearance is consistent
- [ ] Audio matches dialogue timing
- [ ] Voice tone matches scene emotion
- [ ] No audio artifacts or clipping

**UI Requirements:**
- Side-by-side comparison view
- Before/after toggle for replacements
- Audio waveform visualization
- Batch approve/reject controls

---

### 4.7 Step 5: Material Generation (素材生成)

**Description:** Generate all visual and audio assets required for the chapter.

**Configuration:** All models are hot-swappable via Admin configuration.

### 5.1 Image Generation

| Parameter | Description | Options |
|-----------|-------------|---------|
| **Model Provider** | Selected image generation API | Stable Diffusion, Midjourney, DALL-E, etc. |
| **Style Preset** | Visual style template | Anime, Semi-realistic, Watercolor, etc. |
| **Aspect Ratio** | Output dimensions | 16:9, 9:16, 1:1, 4:3 |
| **Resolution** | Image quality | 1024x1024, 1920x1080, etc. |
| **Batch Size** | Images per prompt | 3-5 (configurable) |

**Image Generation Request:**

```json
{
  "panel_id": "uuid",
  "prompt": "Anime style, young woman with long black hair, surprised expression, classroom background, detailed eyes, soft lighting",
  "negative_prompt": "blurry, low quality, distorted face, extra limbs",
  "style_preset": "anime_standard_v2",
  "aspect_ratio": "16:9",
  "resolution": "1920x1080",
  "seed": null,
  "cfg_scale": 7.5,
  "steps": 30
}
```

**Output:** Image assets stored with metadata (generation parameters, timestamps)

### 5.2 Voice Generation (TTS)

| Parameter | Description | Options |
|-----------|-------------|---------|
| **Model Provider** | Selected TTS API | Azure TTS, Google TTS, ElevenLabs, etc. |
| **Voice Actor** | Selected voice profile | Multiple voices per language |
| **Language** | Output language | Chinese (Mandarin), Japanese, etc. |
| **Speed** | Speech rate | 0.5x - 2.0x |
| **Pitch** | Voice pitch adjustment | -12 to +12 semitones |
| **Emotion** | Emotional tone | Neutral, Happy, Sad, Angry, Surprised |

**TTS Generation Request:**

```json
{
  "panel_id": "uuid",
  "text": "你怎么会在这里？",
  "voice_id": "zh-CN-XiaoxiaoNeural",
  "language": "zh-CN",
  "speed": 1.0,
  "pitch": 0,
  "emotion": "surprised",
  "output_format": "wav",
  "sample_rate": 44100
}
```

**Output:** Audio files with timing metadata for lip-sync

**UI Requirements:**
- Model configuration dropdowns
- Generation progress indicator
- Batch generation status dashboard
- Failed generation retry mechanism

---

### 4.8 Step 6: Dynamic Video Generation (动态视频生成)

**Description:** Generate lip-sync accurate video from selected images and audio.

**Input:**
- Selected image per panel
- TTS audio file per panel

**Core Requirement:** Lip movements must be precisely synchronized with audio.

**Video Generation Process:**

| Step | Description | Technology |
|------|-------------|------------|
| **1. Face Detection** | Identify facial landmarks in image | Computer Vision |
| **2. Audio Analysis** | Extract phoneme timing from audio | Audio Processing |
| **3. Lip Movement Mapping** | Map phonemes to viseme (lip shape) sequences | ML Model |
| **4. Frame Interpolation** | Generate intermediate frames for smooth motion | Video Interpolation |
| **5. Video Rendering** | Composite final video with lip movement | Video Encoding |

**Video Generation Configuration:**

| Parameter | Description | Options |
|-----------|-------------|---------|
| **Model Provider** | Video generation API | HeyGen, D-ID, SadTalker, etc. |
| **FPS** | Frames per second | 24, 30, 60 |
| **Resolution** | Output video quality | 720p, 1080p, 4K |
| **Lip-Sync Accuracy** | Precision level | Standard, High, Ultra |
| **Background Motion** | Subtle movement effect | None, Subtle, Dynamic |

**Video Generation Request:**

```json
{
  "panel_id": "uuid",
  "image_id": "uuid",
  "audio_id": "uuid",
  "model_provider": "heygen_v2",
  "fps": 30,
  "resolution": "1920x1080",
  "lip_sync_accuracy": "high",
  "background_motion": "subtle",
  "output_format": "mp4",
  "codec": "h264"
}
```

**Output:** Video file per panel with lip-sync animation

**Validation Rules:**
- Video duration must match audio duration (±0.5s)
- Lip movement must be visible and natural
- No visual artifacts or glitches
- File format: MP4 (H.264 codec)

**UI Requirements:**
- Video preview player
- Lip-sync quality indicator
- Regenerate option for failed generations
- Side-by-side image vs. video comparison

---

### 4.9 Step 7: Smart Composition (智能合成)

**Description:** Assemble video clips with subtitles, voice, and background music.

**Auto-Composition Process:**

| Component | Source | Processing |
|-----------|--------|------------|
| **Video Track** | Step 6 output | Sequential panel videos |
| **Audio Track 1 (Voice)** | Step 5 TTS output | Aligned with video |
| **Audio Track 2 (BGM)** | AI-recommended or selected | Volume-ducked under voice |
| **Subtitle Track** | Script dialogue | Timed to dialogue |
| **Transition Effects** | Template library | Crossfade, cut, etc. |

### BGM Configuration

**AI-Recommended BGM:**

The system analyzes chapter mood and recommends appropriate background music:

| Mood Category | BGM Style | Example Tags |
|---------------|-----------|--------------|
| **Happy/Cheerful** | Upbeat, Major key | Light, Playful, Bright |
| **Sad/Melancholic** | Slow, Minor key | Emotional, Touching, Somber |
| **Tense/Suspenseful** | Dissonant, Irregular | Dark, Mysterious, Intense |
| **Romantic** | Warm, Flowing | Soft, Dreamy, Tender |
| **Action/Energetic** | Fast, Rhythmic | Dynamic, Powerful, Exciting |

**BGM Selection Interface:**

| Feature | Description |
|---------|-------------|
| **Mood Selector** | Select primary and secondary mood tags |
| **BGM Library Browser** | Search and preview available tracks |
| **AI Generate** | Request custom BGM generation |
| **Volume Mixing** | Adjust BGM vs. Voice volume ratio |
| **Fade Controls** | Set intro/outro fade duration |

**AI BGM Generation Request:**

```json
{
  "chapter_id": "uuid",
  "mood_tags": ["romantic", "dreamy"],
  "duration_sec": 180,
  "tempo": "moderate",
  "instruments": ["piano", "strings"],
  "loop_seamless": true
}
```

**Output:** Fully composed chapter video with all audio-visual elements

**UI Requirements:**
- Multi-track timeline view
- BGM preview with volume slider
- Subtitle editor (timing, text, style)
- Export preview before final render

---

### 4.10 Step 8: Chapter Assembly (章节封装)

**Description:** Compile all panel videos into final chapter video.

**Assembly Process:**

1. **Sequence Validation:** Verify all panels are in correct order
2. **Transition Application:** Apply transitions between panels
3. **Audio Normalization:** Ensure consistent audio levels
4. **Chapter Metadata:** Embed title, chapter number, credits
5. **Final Render:** Produce master chapter video file

**Output:** Chapter-level video file ready for final audit

**Chapter Assembly Configuration:**

| Parameter | Description | Default |
|-----------|-------------|---------|
| **Transition Type** | Between panels | Crossfade (0.5s) |
| **Audio Normalization** | Target loudness | -16 LUFS |
| **Title Card** | Chapter intro screen | Auto-generated |
| **End Card** | Chapter ending screen | Optional |
| **Credits** | Cast and crew list | Auto-populated |

**Video Output Specifications:**

| Specification | Value |
|---------------|-------|
| **Container** | MP4 |
| **Video Codec** | H.264 |
| **Audio Codec** | AAC |
| **Resolution** | 1920x1080 (configurable) |
| **Frame Rate** | 30 fps |
| **Bitrate** | 8-12 Mbps |
| **Audio Sample Rate** | 48 kHz |

---

### 4.11 Second Audit Node (第二次审核)

**Owner:** Team Lead (组长)

**Audit Scope:** Final chapter video

**Audit Actions:**

| Action | Description | Consequence |
|--------|-------------|-------------|
| **Approve** | Accept chapter as final | Chapter marked complete, ready for publication |
| **Reject** | Request revisions | Chapter returns to appropriate step with comments |
| **Request Minor Edit** | Quick fixes without full re-review | Team Member can fix without re-audit |

**Rejection Categories:**

| Category | Examples | Return To Step |
|----------|----------|----------------|
| **Visual Quality** | Inconsistent art style, artifacts | Step 5 (Material Gen) |
| **Audio Quality** | Poor TTS, BGM mismatch | Step 5 or 7 |
| **Lip-Sync Issues** | Misaligned mouth movement | Step 6 (Video Gen) |
| **Story/Pacing** | Scene order, timing issues | Step 4 (Storyboard) |
| **Translation/Subtitle** | Typos, timing errors | Step 7 (Composition) |

**Audit Form:**

| Field | Required | Description |
|-------|----------|-------------|
| **Decision** | Yes | Approve / Reject / Minor Edit |
| **Overall Rating** | No | 1-5 stars |
| **Feedback** | If rejected | Detailed comments for revision |
| **Specific Timestamps** | Optional | Reference specific issues |

**UI Requirements:**
- Full-screen video player
- Timestamped comment capability
- Side-by-side comparison (if revised)
- Audit history view

---

## 5. Dual-Audit Workflow

### 5.1 Workflow Overview

```
                                    ┌──────────────────┐
                                    │   Script Locked  │
                                    └────────┬─────────┘
                                             │
                                             ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          FIRST AUDIT (组员)                                  │
│                                                                             │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐                   │
│  │   Step 5    │────>│   Step 6    │────>│   Step 7    │                   │
│  │  Materials  │     │   Video     │     │  Compose    │                   │
│  └─────────────┘     └─────────────┘     └─────────────┘                   │
│         │                                                        │          │
│         └────────────────────────────────────────────────────────┘          │
│                                  │                                          │
│                                  ▼                                          │
│                    ┌─────────────────────────┐                             │
│                    │   Team Member Review    │                             │
│                    │   - Select images       │                             │
│                    │   - Review TTS          │                             │
│                    │   - Check lip-sync      │                             │
│                    │   - Verify composition  │                             │
│                    └───────────┬─────────────┘                             │
│                                │                                            │
│           ┌────────────────────┼────────────────────┐                      │
│           │                    │                    │                      │
│           ▼                    ▼                    ▼                      │
│    ┌─────────────┐     ┌─────────────┐     ┌─────────────┐                │
│    │   APPROVE   │     │   REPLACE   │     │  REGENERATE │                │
│    └──────┬──────┘     └──────┬──────┘     └──────┬──────┘                │
│           │                   │                    │                       │
│           │                   └────────┬───────────┘                       │
│           │                            │                                   │
│           ▼                            ▼                                   │
│    ┌─────────────┐            ┌─────────────┐                             │
│    │  PROCEED TO │            │  STAY IN    │                             │
│    │  STEP 8     │            │  STEP 5-7   │                             │
│    └─────────────┘            └─────────────┘                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                             │
                                             ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         SECOND AUDIT (组长)                                  │
│                                                                             │
│                    ┌─────────────────────────┐                             │
│                    │   Step 8: Chapter       │                             │
│                    │   Assembly Complete     │                             │
│                    └───────────┬─────────────┘                             │
│                                │                                            │
│                                ▼                                            │
│                    ┌─────────────────────────┐                             │
│                    │   Team Lead Review      │                             │
│                    │   - Full chapter video  │                             │
│                    │   - Quality assessment  │                             │
│                    │   - Final approval      │                             │
│                    └───────────┬─────────────┘                             │
│                                │                                            │
│           ┌────────────────────┼────────────────────┐                      │
│           │                    │                    │                      │
│           ▼                    ▼                    ▼                      │
│    ┌─────────────┐     ┌─────────────┐     ┌─────────────┐                │
│    │   APPROVE   │     │   REJECT    │     │ MINOR EDIT  │                │
│    │  PUBLISHED  │     │  (with      │     │  (no        │                │
│    │             │     │   comments) │     │  re-audit)  │                │
│    └─────────────┘     └──────┬──────┘     └──────┬──────┘                │
│                               │                    │                       │
│                               ▼                    ▼                       │
│                      ┌─────────────────────────────────────┐               │
│                      │   Return to appropriate step with   │               │
│                      │   categorized feedback              │               │
│                      └─────────────────────────────────────┘               │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.2 First Audit Specifications

**Auditor:** Team Member (组员)

**Scope:** Steps 5, 6, 7 outputs (Materials, Video, Composition)

**Audit Checklist:**

| Check Item | Criteria | Pass Condition |
|------------|----------|----------------|
| **Image Selection** | All panels have selected images | 100% coverage |
| **Style Consistency** | Visual style matches across panels | No jarring differences |
| **Character Consistency** | Characters look the same throughout | Recognizable same character |
| **TTS Quality** | Voice matches character/emotion | Natural, appropriate tone |
| **Audio Clarity** | No artifacts, clipping, or silence gaps | Clean audio throughout |
| **Lip-Sync Accuracy** | Mouth movement matches audio | Visually synchronized |
| **BGM Fit** | Music matches chapter mood | Emotionally appropriate |
| **Subtitle Accuracy** | Text matches dialogue, timed correctly | No errors |
| **Volume Balance** | Voice audible over BGM | Voice clearly dominant |

**First Audit Workflow:**

1. **Asset Review:** View all generated assets in storyboard layout
2. **Selection:** Choose preferred images from generated options
3. **Quality Check:** Verify audio, lip-sync, composition
4. **Decision:**
   - **Approve:** All items pass checklist → Proceed to Step 8
   - **Replace:** Specific items need changing → Select replacements
   - **Regenerate:** Generation quality insufficient → Request new batch

**Audit Record:**

```json
{
  "audit_id": "uuid",
  "chapter_id": "uuid",
  "auditor_id": "user_uuid",
  "audit_type": "FIRST",
  "timestamp": "2026-03-01T10:30:00Z",
  "status": "APPROVED",
  "approved_panels": [1, 2, 3, 4, 5],
  "rejected_panels": [],
  "comments": "All assets look good. Ready for final review.",
  "time_spent_minutes": 15
}
```

### 5.3 Second Audit Specifications

**Auditor:** Team Lead (组长)

**Scope:** Step 8 output (Final Chapter Video)

**Audit Checklist:**

| Check Item | Criteria | Pass Condition |
|------------|----------|----------------|
| **Overall Quality** | Professional-grade final output | Meets publication standards |
| **Story Coherence** | Chapter flows logically | Clear narrative progression |
| **Pacing** | Scene timing feels natural | No rushed or dragged sections |
| **Audio Mix** | Balanced voice, BGM, SFX | Professional audio quality |
| **Visual Consistency** | No style breaks within chapter | Cohesive visual identity |
| **Subtitle Quality** | Accurate, well-timed, styled | No errors |
| **Technical Quality** | No artifacts, glitches, errors | Clean final render |

**Second Audit Workflow:**

1. **Full Viewing:** Watch complete chapter video without interruption
2. **Detailed Review:** Re-watch with annotation capability
3. **Decision:**
   - **Approve:** Chapter marked complete, ready for publication
   - **Reject:** Return to appropriate step with categorized feedback
   - **Minor Edit:** Team Member can fix without re-audit (typos, timing)

**Rejection Routing:**

| Issue Category | Return To Step | Re-audit Required |
|----------------|----------------|-------------------|
| Image Quality | Step 5 | First Audit |
| TTS Quality | Step 5 | First Audit |
| Lip-Sync Issues | Step 6 | First Audit |
| Storyboard Issues | Step 4 | First Audit |
| BGM Issues | Step 7 | First Audit |
| Subtitle Issues | Step 7 | Minor Edit (no re-audit) |
| Color/Exposure | Step 7 | Minor Edit (no re-audit) |

**Audit Record:**

```json
{
  "audit_id": "uuid",
  "chapter_id": "uuid",
  "auditor_id": "user_uuid",
  "audit_type": "SECOND",
  "timestamp": "2026-03-01T14:00:00Z",
  "status": "APPROVED",
  "rating": 5,
  "feedback": "Excellent work. The lip-sync is particularly good.",
  "rejection_category": null,
  "return_to_step": null,
  "requires_re_audit": false,
  "time_spent_minutes": 25
}
```

### 5.4 Audit State Machine

```
                         ┌─────────────┐
                         │   PENDING   │
                         │  (Waiting)  │
                         └──────┬──────┘
                                │
                                │ Auditor starts review
                                │
                                ▼
                         ┌─────────────┐
                         │  IN_REVIEW  │
                         │ (Active)    │
                         └──────┬──────┘
                                │
                ┌───────────────┼───────────────┐
                │               │               │
                │ APPROVE       │ REJECT        │ │ MINOR_EDIT
                │               │               │
                ▼               ▼               ▼
         ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
         │  APPROVED   │ │  REJECTED   │ │  EDITING    │
         │  (Complete) │ │  (Return)   │ │  (Fix)      │
         └─────────────┘ └──────┬──────┘ └──────┬──────┘
                                │               │
                                │ Fix applied   │
                                │               │
                                └───────────────┘
                                        │
                                        ▼
                                 ┌─────────────┐
                                 │   PENDING   │
                                 │ (Re-review) │
                                 └─────────────┘
```

---

## 6. Dashboard Requirements

### 6.1 Common Modules (All Roles)

| Module | Description | Features |
|--------|-------------|----------|
| **My Tasks** | Personal to-do list | - Task cards with status<br>- Due date indicators<br>- Priority labels<br>- Quick start action |
| **Progress Board** | Visual progress tracking | - Gantt chart view<br>- Kanban board view<br>- Milestone markers |
| **Achievements** | Completion statistics | - Personal completion rate<br>- Badges/achievements<br>- Leaderboard (opt-in) |

### 6.2 Role-Specific Dashboards

### Admin Dashboard

**Purpose:** System oversight, user management, resource monitoring

| Widget | Description | Data Sources |
|--------|-------------|--------------|
| **System Health** | Real-time system status | API uptime, error rates, queue depth |
| **User Management** | User list and roles | User table, role assignments |
| **Project Overview** | All projects status | Project list, member counts, progress |
| **Resource Usage** | API quota consumption | API call logs, quota limits |
| **Audit Logs** | Recent system activity | Audit trail table |
| **Alerts** | System warnings and errors | Alert configuration, incident logs |

**Key Actions:**
- Create/Archive Project
- Add/Remove Users
- Assign Roles
- Configure API Keys
- View Audit Logs
- Manage Quotas

**Layout:**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  ADMIN DASHBOARD                                              [Settings]    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐            │
│  │  System Health  │  │   API Quota     │  │  Active Users   │            │
│  │     ● 99.8%     │  │    78% used     │  │      24         │            │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘            │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │                        PROJECTS OVERVIEW                             │  │
│  │  ┌──────────┬────────┬──────────┬────────┬──────────┐              │  │
│  │  │ Project  │ Status │ Members  │ Progress │ Action  │              │  │
│  │  ├──────────┼────────┼──────────┼────────┼──────────┤              │  │
│  │  │ Manga A  │ Active │    8     │   75%   │  [View] │              │  │
│  │  │ Manga B  │ Active │    5     │   30%   │  [View] │              │  │
│  │  └──────────┴────────┴──────────┴────────┴──────────┘              │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │                         RECENT AUDIT LOGS                           │  │
│  │  [Timestamp] [User] [Action] [Target] [Status]                      │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### Team Lead Dashboard

**Purpose:** Project oversight, team management, quality control

| Widget | Description | Data Sources |
|--------|-------------|--------------|
| **Project Summary** | All projects under lead | Project list, status, deadlines |
| **Team Workload** | Task distribution per member | Task assignments, completion rates |
| **Pending Reviews** | Items awaiting approval | Audit queue, priority sorted |
| **Script Library** | All scripts and versions | Script repository |
| **Quality Metrics** | Approval rates, revision counts | Audit history |
| **Timeline** | Project milestones and deadlines | Project schedule |

**Key Actions:**
- Define/Edit Script
- Configure Pipeline
- Approve/Reject Chapters
- Reassign Tasks
- View Team Performance
- Export Reports

**Layout:**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  TEAM LEAD DASHBOARD                              [New Project] [Settings]  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────┐  ┌─────────────────────────┐                  │
│  │   PENDING REVIEWS       │  │   TEAM WORKLOAD         │                  │
│  │   ⚠️ 3 items awaiting    │  │  ┌────────┬──────────┐ │                  │
│  │                         │  │  │ Member │  Tasks   │ │                  │
│  │   Ch. 5 - First Audit   │  │  ├────────┼──────────┤ │                  │
│  │   Ch. 3 - Second Audit  │  │  │ Wang   │   5/8    │ │                  │
│  │   Ch. 7 - Minor Edit    │  │  │ Li     │   3/6    │ │                  │
│  │                         │  │  │ Zhang  │   7/7    │ │                  │
│  │   [Review Queue →]      │  │  └────────┴──────────┘ │                  │
│  └─────────────────────────┘  └─────────────────────────┘                  │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │                      PROJECT TIMELINE                                │  │
│  │                                                                      │  │
│  │  Manga A  ████████████████████░░░░░░ 75%     Due: Mar 15            │  │
│  │  Manga B  ████████░░░░░░░░░░░░░░░░░░ 30%     Due: Mar 30            │  │
│  │                                                                      │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │                        QUALITY METRICS                               │  │
│  │  First Pass Approval: 82% | Avg Revisions: 1.3 | Avg Rating: 4.2/5 │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### Team Member Dashboard

**Purpose:** Task execution, workflow guidance, audit workspace

| Widget | Description | Data Sources |
|--------|-------------|--------------|
| **My Tasks** | Assigned tasks with status | Task assignments, pipeline state |
| **Task Pipeline** | Visual workflow for current task | Pipeline steps, current position |
| **Quick Actions** | Common actions for active tasks | Context-aware action buttons |
| **Guidance** | Step-by-step instructions | Task type-specific help |
| **My Progress** | Personal completion statistics | Task history, velocity |

**Key Actions:**
- Start Next Task
- Execute Pipeline Steps
- Perform First Audit
- Submit for Review
- Request Help
- View Instructions

**Layout:**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  TEAM MEMBER DASHBOARD                              [Help] [Settings]       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │                    CURRENT TASK                                     │  │
│  │                                                                     │  │
│  │   Project: Manga A | Chapter: 5                                    │  │
│  │                                                                     │  │
│  │   ┌──────────────────────────────────────────────────────────┐     │  │
│  │   │ 1 ✓ 2 ✓ 3 ✓ 4 > 5 ○ 6 ○ 7 ○ 8 ○                         │     │  │
│  │   │    Storyboard   [Current Step: Material Generation]      │     │  │
│  │   └──────────────────────────────────────────────────────────┘     │  │
│  │                                                                     │  │
│  │   [Start Step 5]  [View Instructions]  [Request Help]              │  │
│  │                                                                     │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  ┌─────────────────────────┐  ┌─────────────────────────┐                  │
│  │   UPCOMING TASKS        │  │   COMPLETED             │                  │
│  │                         │  │                         │                  │
│  │   Ch. 6 - Storyboard    │  │   Ch. 4 - Published ✓   │                  │
│  │   Ch. 3 - First Audit   │  │   Ch. 2 - Published ✓   │                  │
│  │   Ch. 8 - Video Gen     │  │   Ch. 1 - Published ✓   │                  │
│  │                         │  │                         │                  │
│  └─────────────────────────┘  └─────────────────────────┘                  │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │                      MY PROGRESS                                    │  │
│  │  Tasks Completed: 24 | Approval Rate: 92% | Avg Time: 2.5h/task   │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 7. Non-Functional Requirements

### 7.1 Multi-Project Support

**Requirement:** Support concurrent execution of multiple manga projects with complete data isolation.

| Aspect | Specification |
|--------|---------------|
| **Data Isolation** | Each project's data (scripts, chapters, assets) must be logically isolated |
| **Access Control** | Users only see projects they are assigned to |
| **Resource Quotas** | Per-project API quota limits configurable by Admin |
| **Parallel Execution** | Multiple projects can generate materials simultaneously |
| **Cross-Project Visibility** | Admins can view all projects; Team Leads see assigned projects only |

**Implementation Considerations:**
- Database schema must include `project_id` on all tenant tables
- API endpoints must validate project access on every request
- File storage must organize assets by project (e.g., `/{project_id}/{chapter_id}/...`)
- Background job queues should support project-based prioritization

---

### 7.2 Full Audit Trail

**Requirement:** Every action in the system must be logged with full traceability and version rollback support.

**Audit Log Schema:**

```json
{
  "log_id": "uuid",
  "timestamp": "ISO8601",
  "user_id": "uuid",
  "user_name": "string",
  "action": "CREATE|UPDATE|DELETE|APPROVE|REJECT|GENERATE|...",
  "entity_type": "PROJECT|SCRIPT|CHAPTER|PANEL|ASSET|...",
  "entity_id": "uuid",
  "previous_state": "JSON|null",
  "current_state": "JSON|null",
  "ip_address": "string",
  "user_agent": "string",
  "metadata": {}
}
```

**Version Control Requirements:**

| Entity | Versioning Strategy | Rollback Support |
|--------|--------------------| ----------------- |
| **Script** | Full content versioning | Yes - any version |
| **Chapter Structure** | Incremental versions | Yes - any version |
| **Storyboard** | Full snapshot per lock | Yes - any version |
| **Selected Images** | Selection history | Yes - previous selections |
| **Audio/TTS** | Generation history | Yes - previous generations |
| **Video** | Render history | Yes - previous renders |

**Rollback Process:**
1. User selects target version from history
2. System shows diff/preview of changes
3. User confirms rollback (with warning)
4. System creates new version (copy of target)
5. Original versions preserved (no deletion)

---

### 7.3 Hot-Swappable Model Configuration

**Requirement:** All AI model providers (LLM, Image, Video, TTS) must be configurable via web UI without code changes.

### Model Provider Abstraction

**Supported Model Categories:**

| Category | Example Providers | Configuration Parameters |
|----------|------------------|-------------------------|
| **LLM** | OpenAI GPT, Anthropic Claude, Google Gemini | API Key, Base URL, Model Name, Max Tokens, Temperature |
| **Image** | Stable Diffusion, Midjourney, DALL-E | API Key, Base URL, Model Name, Style Presets, Resolution |
| **Video** | HeyGen, D-ID, SadTalker | API Key, Base URL, Model Name, FPS, Resolution |
| **TTS** | Azure TTS, ElevenLabs, Google TTS | API Key, Base URL, Voice IDs, Languages, Emotions |

**Configuration UI Requirements:**

| Feature | Description |
|---------|-------------|
| **Provider Selection** | Dropdown of supported providers per category |
| **Credential Input** | Secure fields for API keys (masked, encrypted) |
| **Connection Test** | "Test Connection" button to validate credentials |
| **Model Selection** | Available models from connected provider |
| **Parameter Tuning** | Sliders/inputs for model-specific parameters |
| **Default Assignment** | Set default provider per project or global |

**Configuration Data Model:**

```json
{
  "config_id": "uuid",
  "project_id": "uuid|null",
  "category": "LLM|IMAGE|VIDEO|TTS",
  "provider": "openai|anthropic|stability|...",
  "credentials": {
    "api_key": "encrypted_string",
    "base_url": "https://api.provider.com/v1",
    "organization_id": "optional"
  },
  "default_model": "gpt-4",
  "parameters": {
    "max_tokens": 4096,
    "temperature": 0.7
  },
  "is_active": true,
  "created_at": "ISO8601",
  "updated_at": "ISO8601"
}
```

**Model Interface Abstraction:**

All model providers must implement a common interface:

```python
# Pseudo-code for model provider interface
class ModelProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> GenerationResult:
        pass

    @abstractmethod
    def validate_connection(self) -> bool:
        pass

    @abstractmethod
    def list_models(self) -> List[ModelInfo]:
        pass

    @abstractmethod
    def get_quota_usage(self) -> QuotaInfo:
        pass
```

---

### 7.4 Performance Requirements

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Page Load Time** | < 2 seconds (first screen) | Frontend performance monitoring |
| **API Response Time (P95)** | < 500ms | Backend monitoring (excluding AI API calls) |
| **AI Generation Queue Time** | < 30 seconds | Job queue monitoring |
| **Concurrent Users** | Support 100+ simultaneous users | Load testing |
| **Video Rendering Time** | < 5 minutes per chapter video | Background job monitoring |
| **System Availability** | > 99.5% uptime | Infrastructure monitoring |

---

### 7.5 Security Requirements

| Requirement | Description |
|-------------|-------------|
| **Authentication** | JWT-based authentication with refresh tokens |
| **Authorization** | Role-based access control (RBAC) enforced on all endpoints |
| **Data Encryption** | API keys encrypted at rest (AES-256) |
| **HTTPS** | All traffic encrypted in transit |
| **Input Validation** | All user inputs validated and sanitized |
| **Rate Limiting** | API rate limiting per user and per project |
| **Audit Logging** | All authentication and authorization events logged |

---

### 7.6 Storage Quotas and Limits

**Purpose:** Define clear storage boundaries to manage infrastructure costs and ensure fair resource allocation.

#### Per-Project Storage Limits

| Project Tier | Storage Limit | Monthly API Call Limit | Max Chapters | Max Team Members |
|--------------|---------------|------------------------|--------------|------------------|
| **Starter** | 10 GB | 1,000 | 20 | 5 |
| **Professional** | 100 GB | 10,000 | 100 | 20 |
| **Enterprise** | 1 TB | 100,000 | Unlimited | Unlimited |

**Storage Breakdown:**
- Images: ~2-5 MB per image (1024x1024 PNG)
- Audio: ~1-3 MB per minute (WAV/MP3)
- Video: ~50-100 MB per minute (1080p MP4)
- Project data (JSON): ~100 KB per project

#### Per-User Upload Limits

| Resource Type | Daily Upload Limit | Per-File Size Limit |
|---------------|-------------------|---------------------|
| **Images (User Uploaded)** | 100 files | 10 MB |
| **Audio (User Uploaded)** | 50 files | 50 MB |
| **Video (User Uploaded)** | 20 files | 500 MB |
| **Scripts/Documents** | Unlimited | 10 MB |

#### File Size Limits

| File Type | Maximum Size | Supported Formats |
|-----------|--------------|-------------------|
| **Script Upload** | 10 MB | .txt, .docx, .pdf |
| **Reference Images** | 10 MB | .png, .jpg, .webp |
| **Character Sheets** | 10 MB | .png, .jpg, .psd |
| **BGM Upload** | 50 MB | .mp3, .wav, .aac, .ogg |
| **SFX Upload** | 50 MB | .mp3, .wav, .aac |
| **Video Export** | 2 GB | .mp4, .mov |
| **Project Archive** | 5 GB | .zip |

**Storage Management Features:**
- Storage usage dashboard per project
- Warning alerts at 80% capacity
- Automatic cleanup of unselected generations (after 7 days)
- Archive cold data to cheaper storage tier (after 30 days)

---

### 7.7 WebSocket Real-Time Communication

**Purpose:** Enable real-time progress updates for long-running AI generation tasks.

#### Connection Handshake

**WebSocket Endpoint:** `wss://api.domain.com/ws/v1/notifications`

**Connection Request:**
```json
{
  "type": "CONNECTION_INIT",
  "payload": {
    "authorization": "Bearer <JWT_ACCESS_TOKEN>"
  }
}
```

**Server Acknowledgment:**
```json
{
  "type": "CONNECTION_ACK",
  "payload": {
    "connectionId": "uuid",
    "expiresIn": 3600
  }
}
```

**Connection Error:**
```json
{
  "type": "CONNECTION_ERROR",
  "payload": {
    "code": "UNAUTHORIZED",
    "message": "Invalid or expired token"
  }
}
```

#### Message Format

**Progress Update:**
```json
{
  "type": "PROGRESS_UPDATE",
  "payload": {
    "jobId": "uuid",
    "jobType": "IMAGE_GENERATION|AUDIO_GENERATION|VIDEO_GENERATION|COMPOSITION",
    "status": "QUEUED|PROCESSING|COMPLETED|FAILED",
    "progress": 0.75,
    "currentStep": "Generating image variations...",
    "totalSteps": 4,
    "completedSteps": 3,
    "estimatedTimeRemaining": 15,
    "data": {
      "panelId": "uuid",
      "generatedCount": 3,
      "expectedCount": 4
    }
  }
}
```

**Error Notification:**
```json
{
  "type": "ERROR",
  "payload": {
    "code": "PROVIDER_RATE_LIMITED",
    "message": "Image generation API rate limit exceeded",
    "jobId": "uuid",
    "retryable": true,
    "retryAfter": 60,
    "suggestedAction": "Retry in 60 seconds or switch provider"
  }
}
```

**Task Completion:**
```json
{
  "type": "TASK_COMPLETE",
  "payload": {
    "jobId": "uuid",
    "jobType": "IMAGE_GENERATION",
    "status": "COMPLETED",
    "result": {
      "generatedItems": [
        {"id": "uuid", "url": "https://...", "thumbnailUrl": "https://..."}
      ],
      "metadata": {
        "generationTime": 45.2,
        "provider": "stability_ai"
      }
    }
  }
}
```

#### Reconnection Strategy

| Scenario | Client Action | Backoff |
|----------|---------------|---------|
| **Connection Lost** | Auto-reconnect | Exponential backoff (1s, 2s, 4s, 8s, max 30s) |
| **Token Expired** | Refresh token, then reconnect | Immediate after refresh |
| **Server Error (5xx)** | Auto-reconnect | Exponential backoff with jitter |
| **Client Error (4xx)** | Do not reconnect | Manual intervention required |

**Heartbeat Mechanism:**
- Client sends `PING` every 30 seconds
- Server responds with `PONG`
- If no `PONG` received within 10 seconds, client reconnects

```json
// Client -> Server
{"type": "PING", "timestamp": "ISO8601"}

// Server -> Client
{"type": "PONG", "timestamp": "ISO8601"}
```

---

### 7.8 AI Provider Fallback and Retry Logic

**Purpose:** Ensure generation continuity when AI providers experience issues.

#### Automatic Retry Logic

| Failure Type | Retry Count | Delay Between Retries | Timeout Per Attempt |
|--------------|-------------|----------------------|---------------------|
| **Network Error** | 3 | Exponential (1s, 2s, 4s) | 30 seconds |
| **Rate Limit (429)** | 3 | Value from Retry-After header | 30 seconds |
| **Server Error (5xx)** | 3 | Exponential (2s, 4s, 8s) | 60 seconds |
| **Invalid Request (4xx)** | 0 | N/A | 10 seconds |

**Retry Configuration:**
```json
{
  "retryPolicy": {
    "maxRetries": 3,
    "initialDelayMs": 1000,
    "maxDelayMs": 8000,
    "multiplier": 2,
    "jitter": 0.1,
    "timeoutMs": 30000,
    "retryableStatusCodes": [429, 500, 502, 503, 504],
    "retryableErrorCodes": ["NETWORK_ERROR", "TIMEOUT"]
  }
}
```

#### Provider Failover Strategy

**Priority-Based Failover:**
```
Primary Provider (configured)
    ↓ (after 3 failed retries)
Secondary Provider (auto-selected from available providers)
    ↓ (after 3 failed retries)
Manual Intervention Required
```

**Provider Health Check:**
- System checks provider status every 5 minutes
- Providers with >50% failure rate marked as "DEGRADED"
- Providers with >90% failure rate marked as "UNAVAILABLE"

#### Manual Provider Switch Workflow

**User-Initiated Switch:**

1. User views failed generation job
2. Clicks "Switch Provider" button
3. Modal shows available alternative providers
4. User selects provider and confirms
5. Job restarts with new provider from failed step

**Provider Switch UI:**
```
┌─────────────────────────────────────────────────────────┐
│  Generation Failed - Switch Provider                    │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Job: Image Generation for Panel 3                      │
│  Failed Provider: Stability AI                          │
│  Error: Rate limit exceeded                             │
│                                                         │
│  Available Alternative Providers:                       │
│                                                         │
│  ○ Midjourney API    Status: ● Healthy   Est: 45s      │
│  ○ DALL-E 3          Status: ● Healthy   Est: 30s      │
│  ○ Leonardo.ai       Status: ○ Degraded  Est: 60s      │
│                                                         │
│  [Cancel Job]  [Switch to Midjourney]  [Switch to DALL-E] │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

### 7.9 Task Assignment and Workflow

**Purpose:** Define clear task assignment mechanisms for team coordination.

#### Task Assignment Modes

**Auto-Assignment Mode:**
- System assigns tasks based on role and availability
- Round-robin distribution among team members
- Considers current workload (pending task count)
- Factors in task priority and deadline urgency

**Auto-Assignment Algorithm:**
```
1. Filter eligible team members (role = TEAM_MEMBER AND active)
2. Sort by workload_score (pending_tasks ASC, completion_rate DESC)
3. Assign to lowest-score member
4. Update workload_score
```

**Manual Assignment Mode:**
- Team Lead manually assigns tasks to specific members
- Can reassign tasks at any time
- Can set task priority and deadline

#### Task Visibility

| Role | Can View | Can Edit | Can Reassign |
|------|----------|----------|--------------|
| **Admin** | All projects | All tasks | All tasks |
| **Team Lead** | Assigned projects | Own + team tasks | Team tasks |
| **Team Member** | Own tasks | Own tasks | N/A |

**Task Visibility Rules:**
- Team members can see each other's task status (not content)
- Task content (materials, edits) visible only to assignee and Team Lead
- Completed tasks visible to all team members for reference

#### Task Priority and Deadline Handling

**Priority Levels:**

| Priority | Color | SLA | Notification |
|----------|-------|-----|--------------|
| **Critical** | Red | 4 hours | Immediate push + email |
| **High** | Orange | 24 hours | Immediate push |
| **Normal** | Blue | 48 hours | Daily digest |
| **Low** | Gray | 7 days | Weekly digest |

**Deadline Escalation:**

| Time Remaining | Action |
|----------------|--------|
| 50% elapsed | Progress reminder notification |
| 75% elapsed | Warning to assignee |
| 90% elapsed | Alert to assignee + Team Lead |
| 100% elapsed (overdue) | Escalation to Team Lead, task marked overdue |
| +24 hours overdue | Escalation to Admin |

**Task Assignment Data Model:**
```json
{
  "task_id": "uuid",
  "project_id": "uuid",
  "chapter_id": "uuid",
  "task_type": "CHAPTER_BREAKDOWN|STORYBOARD|FIRST_AUDIT|VIDEO_GEN",
  "assignee_id": "uuid|null",
  "assigned_by": "uuid",
  "priority": "CRITICAL|HIGH|NORMAL|LOW",
  "status": "PENDING|ASSIGNED|IN_PROGRESS|COMPLETED|OVERDUE",
  "due_at": "ISO8601",
  "started_at": "ISO8601|null",
  "completed_at": "ISO8601|null",
  "estimated_hours": 2.0,
  "actual_hours": null,
  "workflow_step": 4,
  "metadata": {
    "auto_assigned": true,
    "previous_assignee": null,
    "reassignment_count": 0
  }
}
```

---

### 7.10 Scalability Requirements

| Aspect | Requirement |
|--------|-------------|
| **Horizontal Scaling** | Statelesss backend services for horizontal scaling |
| **Database** | Read replicas for heavy read workloads |
| **File Storage** | Object storage (S3-compatible) for media assets |
| **Background Jobs** | Distributed job queue for AI generation tasks |
| **CDN** | Media delivery via CDN for low-latency access |

---

### 7.11 Export and Distribution Requirements

**Purpose:** Define export formats and distribution options for completed chapters and projects.

#### Video Export Formats

**Standard Export Formats:**

| Format | Use Case | Resolution | Codec | Container | Max File Size |
|--------|----------|------------|-------|-----------|---------------|
| **MP4 (H.264)** | Web streaming, general distribution | 1080p, 720p | H.264 | MP4 | 2 GB |
| **MP4 (H.265/HEVC)** | High quality, smaller file size | 4K, 1080p | H.265 | MP4 | 4 GB |
| **MOV (ProRes)** | Professional editing, archival | 4K, 1080p | ProRes 422 | MOV | 10 GB |
| **WebM (VP9)** | Web optimization | 1080p, 720p | VP9 | WebM | 1 GB |

**Export Quality Presets:**

| Preset | Resolution | Bitrate | Frame Rate | Use Case |
|--------|------------|---------|------------|----------|
| **Mobile** | 720p | 3 Mbps | 24 fps | Mobile apps, messaging |
| **Web Standard** | 1080p | 8 Mbps | 30 fps | YouTube, social media |
| **High Quality** | 1080p | 15 Mbps | 60 fps | Premium platforms |
| **Master** | 4K | 50 Mbps | 60 fps | Archival, broadcast |

**Export Configuration:**
```json
{
  "export_id": "uuid",
  "chapter_id": "uuid",
  "format": "MP4_H264|MP4_HEVC|MOV_PRORES|WEBM_VP9",
  "preset": "MOBILE|WEB_STANDARD|HIGH_QUALITY|MASTER",
  "resolution": "1920x1080",
  "include_subtitles": true,
  "subtitle_format": "BURNED_IN|SRT_FILE|VTT_FILE",
  "include_chapter_markers": true,
  "include_metadata": true,
  "audio_channels": "STEREO|MONO|5.1_SURROUND"
}
```

#### Batch Export Support

**Batch Export Scenarios:**

| Scenario | Description | Max Batch Size |
|----------|-------------|----------------|
| **Chapter Batch** | Export multiple chapters from single project | 50 chapters |
| **Project Export** | Export all chapters in multiple formats | 10 formats total |
| **Format Variants** | Same chapter, multiple format/resolution combos | 5 variants |

**Batch Export Workflow:**

1. User selects chapters/format variants
2. System estimates total time and storage
3. User confirms and export starts
4. Progress shown per item in batch
5. Notification when complete
6. Download all as single archive or individual files

**Batch Export Status:**
```json
{
  "batch_id": "uuid",
  "project_id": "uuid",
  "requested_by": "uuid",
  "status": "PROCESSING|COMPLETED|PARTIAL|FAILED",
  "total_items": 10,
  "completed_items": 7,
  "failed_items": 1,
  "items": [
    {
      "chapter_id": "uuid",
      "format": "MP4_H264",
      "status": "COMPLETED",
      "download_url": "https://...",
      "file_size_mb": 245
    }
  ],
  "archive_url": "https://... (when all complete)",
  "created_at": "ISO8601",
  "completed_at": "ISO8601|null"
}
```

#### Project Archive Format

**Full Project Archive:**

Includes all project data for backup or migration:

| Component | Format | Description |
|-----------|--------|-------------|
| **Project Metadata** | JSON | Project settings, team, configs |
| **Scripts** | JSON + PDF | All versions with audit trail |
| **Chapters** | JSON | Structure, storyboards, panels |
| **Generated Assets** | Original formats | Images (PNG), Audio (WAV), Video (MP4) |
| **Audit Logs** | JSON | Complete history |
| **Model Configs** | JSON (redacted) | Provider settings (credentials excluded) |

**Archive Structure:**
```
project_{id}_archive.zip
├── manifest.json           # Archive metadata
├── project/
│   ├── metadata.json
│   ├── settings.json
│   └── team.json
├── scripts/
│   ├── script_v1.json
│   ├── script_v2.json
│   └── script_final.json
├── chapters/
│   ├── chapter_01/
│   │   ├── metadata.json
│   │   ├── storyboard.json
│   │   ├── panels/
│   │   ├── images/
│   │   ├── audio/
│   │   └── video/
│   └── chapter_02/
├── audits/
│   └── audit_logs.json
└── exports/
    └── rendered_videos/
```

**Archive Sizes (Estimated):**

| Project Size | Chapters | Archive Size | Export Time |
|--------------|----------|--------------|-------------|
| **Small** | 1-10 | 1-5 GB | 5-15 min |
| **Medium** | 11-50 | 10-50 GB | 30-60 min |
| **Large** | 51-100 | 50-200 GB | 2-4 hours |

**Import/Restore Support:**
- Validate archive integrity before import
- Check for ID conflicts with existing data
- Option to merge or overwrite existing project
- Restore audit trail and version history

#### Distribution Integration

**Direct Platform Upload (Future Phase 2):**

| Platform | Supported | Auto-Upload | Metadata Sync |
|----------|-----------|-------------|---------------|
| **YouTube** | Planned | Yes | Title, description, tags |
| **Bilibili** | Planned | Yes | Title, description, categories |
| **Vimeo** | Planned | Yes | Privacy settings, embed options |
| **TikTok** | Planned | Manual | N/A |
| **Instagram Reels** | Planned | Manual | N/A |

---

## 8. API Requirements

### 8.1 API Design Principles

- **RESTful Design:** Resource-based URLs, standard HTTP methods
- **JSON Format:** Request/response bodies in JSON
- **Authentication:** Bearer token (JWT) in Authorization header
- **Versioning:** URL prefix versioning (`/api/v1/...`)
- **Pagination:** Cursor-based pagination for list endpoints
- **Error Handling:** Standardized error response format

### 8.2 Standard Response Format

**Success Response:**

```json
{
  "success": true,
  "data": { },
  "meta": {
    "request_id": "uuid",
    "timestamp": "ISO8601"
  }
}
```

**Error Response:**

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable message",
    "details": { }
  },
  "meta": {
    "request_id": "uuid",
    "timestamp": "ISO8601"
  }
}
```

---

### 8.3 Key API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/login` | User login, returns JWT |
| POST | `/api/v1/auth/refresh` | Refresh access token |
| POST | `/api/v1/auth/logout` | Invalidate token |

---

### Projects

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/projects` | List projects (filtered by user access) |
| POST | `/api/v1/projects` | Create new project |
| GET | `/api/v1/projects/{id}` | Get project details |
| PUT | `/api/v1/projects/{id}` | Update project |
| DELETE | `/api/v1/projects/{id}` | Archive project |
| GET | `/api/v1/projects/{id}/members` | Get project members |
| POST | `/api/v1/projects/{id}/members` | Add member to project |

**Request/Example:**

```json
// POST /api/v1/projects
{
  "name": "Manga Series A",
  "description": "Action manga series",
  "team_lead_id": "user_uuid",
  "model_config_ids": {
    "llm": "config_uuid",
    "image": "config_uuid",
    "video": "config_uuid",
    "tts": "config_uuid"
  }
}
```

---

### Scripts

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/scripts` | List scripts for project |
| POST | `/api/v1/scripts` | Create script (upload or generate) |
| GET | `/api/v1/scripts/{id}` | Get script details |
| PUT | `/api/v1/scripts/{id}` | Update script |
| POST | `/api/v1/scripts/{id}/generate` | Generate script via LLM |
| POST | `/api/v1/scripts/{id}/lock` | Lock script (triggers Chapter Breakdown) |
| POST | `/api/v1/scripts/{id}/unlock` | Unlock script |
| GET | `/api/v1/scripts/{id}/versions` | Get version history |
| POST | `/api/v1/scripts/{id}/rollback` | Rollback to version |

**Request/Example:**

```json
// POST /api/v1/scripts/{id}/generate
{
  "prompt": "A story about a high school student who discovers magical powers",
  "tone": "adventure",
  "target_length": "feature",
  "llm_config_id": "config_uuid"
}

// Response
{
  "success": true,
  "data": {
    "script_id": "uuid",
    "status": "GENERATING",
    "estimated_time_sec": 30
  }
}
```

---

### Chapters

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/scripts/{script_id}/chapters` | List chapters |
| POST | `/api/v1/chapters` | Create chapter manually |
| GET | `/api/v1/chapters/{id}` | Get chapter details |
| PUT | `/api/v1/chapters/{id}` | Update chapter |
| POST | `/api/v1/chapters/reorder` | Reorder chapters |
| POST | `/api/v1/chapters/{id}/split` | Split chapter |
| POST | `/api/v1/chapters/{id}/merge` | Merge chapters |

---

### Storyboards

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/chapters/{id}/storyboard` | Get storyboard panels |
| POST | `/api/v1/chapters/{id}/storyboard/generate` | Auto-generate storyboard |
| PUT | `/api/v1/storyboard/panels/{id}` | Update panel |
| POST | `/api/v1/storyboard/panels` | Add new panel |
| DELETE | `/api/v1/storyboard/panels/{id}` | Delete panel |
| POST | `/api/v1/storyboard/panels/reorder` | Reorder panels |
| POST | `/api/v1/chapters/{id}/storyboard/lock` | Lock storyboard |

---

### Material Generation

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/generation/images` | Generate images for panels |
| POST | `/api/v1/generation/audio` | Generate TTS audio |
| POST | `/api/v1/generation/video` | Generate lip-sync video |
| GET | `/api/v1/generation/jobs/{id}` | Get generation job status |
| POST | `/api/v1/generation/jobs/{id}/cancel` | Cancel generation job |

**Request/Example:**

```json
// POST /api/v1/generation/images
{
  "panel_ids": ["uuid1", "uuid2"],
  "batch_size": 4,
  "image_config_id": "config_uuid",
  "style_preset": "anime_standard"
}

// Response
{
  "success": true,
  "data": {
    "job_id": "uuid",
    "status": "QUEUED",
    "estimated_time_sec": 120
  }
}
```

---

### Audits

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/audits/pending` | Get pending audits for user |
| POST | `/api/v1/audits/first` | Submit first audit |
| POST | `/api/v1/audits/second` | Submit second audit |
| GET | `/api/v1/audits/history/{chapter_id}` | Get audit history |

**Request/Example:**

```json
// POST /api/v1/audits/second
{
  "chapter_id": "uuid",
  "decision": "APPROVED",
  "rating": 5,
  "feedback": "Excellent quality",
  "rejection_category": null
}
```

---

### Model Configuration

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/model-configs` | List model configurations |
| POST | `/api/v1/model-configs` | Create new configuration |
| GET | `/api/v1/model-configs/{id}` | Get configuration details |
| PUT | `/api/v1/model-configs/{id}` | Update configuration |
| DELETE | `/api/v1/model-configs/{id}` | Delete configuration |
| POST | `/api/v1/model-configs/{id}/test` | Test connection |
| GET | `/api/v1/model-configs/providers` | List supported providers |

---

### Dashboard

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/dashboard/summary` | Get dashboard summary |
| GET | `/api/v1/dashboard/tasks` | Get user's tasks |
| GET | `/api/v1/dashboard/progress` | Get progress metrics |
| GET | `/api/v1/dashboard/notifications` | Get notifications |

---

## 9. Data Model Overview

### 9.1 Entity Relationship Diagram

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│     USER        │     │     PROJECT     │     │   MODEL_CONFIG  │
├─────────────────┤     ├─────────────────┤     ├─────────────────┤
│ id (PK)         │     │ id (PK)         │     │ id (PK)         │
│ email           │     │ name            │     │ project_id (FK) │
│ name            │     │ description     │     │ category        │
│ role            │     │ team_lead_id(FK)│     │ provider        │
│ created_at      │     │ status          │     │ credentials     │
└────────┬────────┘     │ created_at      │     │ parameters      │
         │              └────────┬────────┘     │ created_at      │
         │                       │               └─────────────────┘
         │                       │
         │              ┌────────┴────────┐
         │              │                 │
         │              ▼                 ▼
         │       ┌─────────────────┐     ┌─────────────────┐
         │       │   PROJECT_MEMBER│     │     SCRIPT      │
         │       ├─────────────────┤     ├─────────────────┤
         └──────>│ user_id (FK)    │     │ id (PK)         │
                 │ project_id (FK) │     │ project_id (FK) │
                 │ role            │     │ title           │
                 │ joined_at       │     │ content         │
                 └─────────────────┘     │ status          │
                                         │ version         │
                                         │ locked_at       │
                                         └────────┬────────┘
                                                  │
                                                  │ 1:N
                                                  ▼
                                         ┌─────────────────┐
                                         │     CHAPTER     │
                                         ├─────────────────┤
                                         │ id (PK)         │
                                         │ script_id (FK)  │
                                         │ chapter_number  │
                                         │ title           │
                                         │ summary         │
                                         │ sequence_order  │
                                         │ status          │
                                         └────────┬────────┘
                                                  │
                                                  │ 1:N
                                                  ▼
                                         ┌─────────────────┐
                                         │   STORYBOARD    │
                                         │     PANEL       │
                                         ├─────────────────┤
                                         │ id (PK)         │
                                         │ chapter_id (FK) │
                                         │ sequence_number │
                                         │ image_prompt    │
                                         │ camera_direction│
                                         │ dialogue        │
                                         │ selected_image  │
                                         │ selected_audio  │
                                         │ status          │
                                         └────────┬────────┘
                                                  │
                    ┌─────────────────────────────┼─────────────────────────────┐
                    │                             │                             │
                    ▼                             ▼                             ▼
         ┌─────────────────┐           ┌─────────────────┐           ┌─────────────────┐
         │  GENERATED_     │           │  GENERATED_     │           │  GENERATED_     │
         │    IMAGE        │           │    AUDIO        │           │    VIDEO        │
         ├─────────────────┤           ├─────────────────┤           ├─────────────────┤
         │ id (PK)         │           │ id (PK)         │           │ id (PK)         │
         │ panel_id (FK)   │           │ panel_id (FK)   │           │ panel_id (FK)   │
         │ image_url       │           │ audio_url       │           │ video_url       │
         │ generation_params│          │ generation_params│          │ generation_params│
         │ is_selected     │           │ is_selected     │           │ duration_sec    │
         │ created_at      │           │ created_at      │           │ created_at      │
         └─────────────────┘           └─────────────────┘           └─────────────────┘
                                                  │
                                                  ▼
                                         ┌─────────────────┐
                                         │     AUDIT       │
                                         │     LOG         │
                                         ├─────────────────┤
                                         │ id (PK)         │
                                         │ chapter_id (FK) │
                                         │ auditor_id (FK) │
                                         │ audit_type      │
                                         │ decision        │
                                         │ feedback        │
                                         │ created_at      │
                                         └─────────────────┘
```

### 9.2 Core Entity Definitions

**User:**
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL, -- ADMIN, TEAM_LEAD, TEAM_MEMBER
    avatar_url VARCHAR(500),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Project:**
```sql
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    team_lead_id UUID REFERENCES users(id),
    status VARCHAR(50) DEFAULT 'ACTIVE', -- ACTIVE, ARCHIVED
    settings JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Model Configuration:**
```sql
CREATE TABLE model_configs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id),
    category VARCHAR(50) NOT NULL, -- LLM, IMAGE, VIDEO, TTS
    provider VARCHAR(100) NOT NULL,
    credentials JSONB NOT NULL, -- Encrypted
    default_model VARCHAR(100),
    parameters JSONB,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Script:**
```sql
CREATE TABLE scripts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    content JSONB NOT NULL, -- Structured script format
    version INTEGER DEFAULT 1,
    status VARCHAR(50) DEFAULT 'DRAFT', -- DRAFT, LOCKED, PUBLISHED
    locked_at TIMESTAMP,
    locked_by UUID REFERENCES users(id),
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Chapter:**
```sql
CREATE TABLE chapters (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    script_id UUID REFERENCES scripts(id) ON DELETE CASCADE,
    chapter_number INTEGER NOT NULL,
    title VARCHAR(255),
    summary TEXT,
    sequence_order INTEGER NOT NULL,
    estimated_duration_sec INTEGER,
    actual_duration_sec INTEGER,
    status VARCHAR(50) DEFAULT 'PENDING',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(script_id, chapter_number)
);
```

**Storyboard Panel:**
```sql
CREATE TABLE storyboard_panels (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chapter_id UUID REFERENCES chapters(id) ON DELETE CASCADE,
    sequence_number INTEGER NOT NULL,
    image_prompt TEXT,
    camera_direction VARCHAR(100),
    character_pose VARCHAR(100),
    background_description TEXT,
    dialogue TEXT,
    subtitle_text VARCHAR(500),
    estimated_duration_sec DECIMAL(5,2),
    selected_image_id UUID,
    selected_audio_id UUID,
    status VARCHAR(50) DEFAULT 'PENDING',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Generated Assets:**
```sql
CREATE TABLE generated_images (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    panel_id UUID REFERENCES storyboard_panels(id) ON DELETE CASCADE,
    image_url VARCHAR(500) NOT NULL,
    thumbnail_url VARCHAR(500),
    generation_params JSONB,
    seed INTEGER,
    is_selected BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE generated_audio (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    panel_id UUID REFERENCES storyboard_panels(id) ON DELETE CASCADE,
    audio_url VARCHAR(500) NOT NULL,
    duration_sec DECIMAL(8,2),
    voice_id VARCHAR(100),
    generation_params JSONB,
    is_selected BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE generated_videos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    panel_id UUID REFERENCES storyboard_panels(id) ON DELETE CASCADE,
    video_url VARCHAR(500) NOT NULL,
    thumbnail_url VARCHAR(500),
    duration_sec DECIMAL(8,2),
    generation_params JSONB,
    lip_sync_accuracy VARCHAR(50),
    status VARCHAR(50) DEFAULT 'GENERATING',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Audit Log:**
```sql
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chapter_id UUID REFERENCES chapters(id),
    auditor_id UUID REFERENCES users(id),
    audit_type VARCHAR(50) NOT NULL, -- FIRST, SECOND
    decision VARCHAR(50) NOT NULL, -- APPROVED, REJECTED, MINOR_EDIT
    rating INTEGER, -- 1-5 for second audit
    feedback TEXT,
    rejection_category VARCHAR(100),
    return_to_step INTEGER,
    requires_re_audit BOOLEAN DEFAULT true,
    time_spent_minutes INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE system_audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id UUID REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(100),
    entity_id UUID,
    previous_state JSONB,
    current_state JSONB,
    ip_address VARCHAR(50),
    user_agent TEXT,
    metadata JSONB
);
```

---

## 10. Acceptance Criteria

### 10.1 Pipeline Workflow

| Feature | Acceptance Criteria |
|---------|---------------------|
| **Script Generation** | Given a valid prompt, when LLM generation is requested, then a structured script is returned within 60 seconds |
| **Script Lock** | Given a valid script, when locked, then Chapter Breakdown is automatically triggered and chapters are created |
| **Chapter Breakdown** | Given a locked script, when auto-generation runs, then chapters are created with logical breaks and auto-generated titles |
| **Storyboard Generation** | Given a chapter, when storyboard generation is requested, then panels are created with prompts, directions, and dialogue |
| **Image Generation** | Given storyboard panels, when image generation is requested, then 3-5 images per panel are generated and stored |
| **TTS Generation** | Given panel dialogue, when audio generation is requested, then audio files are created with correct timing |
| **Video Generation** | Given selected images and audio, when video generation is requested, then lip-sync videos are created with <0.5s duration variance |
| **Smart Composition** | Given all assets, when composition is requested, then a complete video with BGM and subtitles is produced |
| **Chapter Assembly** | Given composed panels, when assembly is requested, then a single chapter video file is rendered |

### 10.2 Dual-Audit System

| Feature | Acceptance Criteria |
|---------|---------------------|
| **First Audit Access** | Given a Team Member role, when materials are ready, then the first audit interface is accessible |
| **Image Selection** | Given multiple generated images, when user selects one, then it is marked as selected and others are archived |
| **First Audit Approval** | Given all panels reviewed, when approved, then the chapter proceeds to Second Audit |
| **Second Audit Access** | Given a Team Lead role, when chapter is submitted, then the final audit interface is accessible |
| **Second Audit Approval** | Given a chapter video, when approved, then the chapter status is set to PUBLISHED |
| **Second Audit Rejection** | Given a chapter video with issues, when rejected with feedback, then the chapter returns to the appropriate step |
| **Audit History** | Given any chapter, when viewing history, then all audit records with decisions and feedback are displayed |

### 10.3 Dashboard Features

| Feature | Acceptance Criteria |
|---------|---------------------|
| **Task List** | Given a logged-in user, when viewing dashboard, then tasks are displayed filtered by role and assignment |
| **Progress Visualization** | Given project data, when viewing progress, then accurate completion percentages and timelines are shown |
| **Pending Reviews** | Given pending audits, when Team Lead views dashboard, then items are listed with priority and due dates |
| **Quick Actions** | Given an active task, when viewing dashboard, then context-aware action buttons are displayed |

### 10.4 Multi-Project Support

| Feature | Acceptance Criteria |
|---------|---------------------|
| **Project Isolation** | Given multiple projects, when user accesses data, then only data from assigned projects is visible |
| **Parallel Execution** | Given two projects generating materials, when both run simultaneously, then both complete without interference |
| **Project Switching** | Given access to multiple projects, when switching projects, then the UI updates to show correct project data |

### 10.5 Audit Trail

| Feature | Acceptance Criteria |
|---------|---------------------|
| **Action Logging** | Given any user action, when executed, then an audit log entry is created with full context |
| **Version History** | Given a script with multiple edits, when viewing history, then all versions are listed with timestamps and authors |
| **Rollback** | Given a previous version, when rollback is requested, then a new version is created as a copy of the target |

### 10.6 Model Configuration

| Feature | Acceptance Criteria |
|---------|---------------------|
| **Provider Configuration** | Given valid API credentials, when saved, then the configuration is stored encrypted |
| **Connection Test** | Given API credentials, when test is requested, then connection is validated and result is displayed |
| **Hot Swap** | Given an active generation, when model config is changed, then new generations use the new configuration |
| **Per-Project Config** | Given multiple projects, when configuring models, then each project can have independent model settings |

### 10.7 Performance

| Feature | Acceptance Criteria |
|---------|---------------------|
| **Page Load** | Given a standard dashboard page, when loaded, then first screen renders within 2 seconds |
| **API Response** | Given standard API requests, when measured, then P95 response time is under 500ms (excluding AI calls) |
| **Concurrent Users** | Given 100 simultaneous users, when performing typical actions, then system remains responsive with <5s response times |

### 10.8 Security

| Feature | Acceptance Criteria |
|---------|---------------------|
| **Authentication** | Given invalid credentials, when login is attempted, then access is denied with appropriate error |
| **Authorization** | Given a Team Member, when accessing Admin endpoints, then access is denied with 403 Forbidden |
| **Data Isolation** | Given Project A user, when querying Project B data, then no data is returned |
| **Credential Encryption** | Given API keys in database, when queried directly, then credentials are encrypted |

---

## Appendix A: Glossary

| Term | Definition |
|------|------------|
| **Pipeline** | The 8-step workflow for manga video production |
| **Dual-Audit** | Two-level review system (First by Team Member, Second by Team Lead) |
| **Storyboard Panel** | Individual frame/unit within a chapter containing visual and audio directions |
| **抽卡制 (Card Draw)** | Image selection mechanism where multiple options are generated per panel |
| **Lip-Sync** | Synchronization of character mouth movements with audio dialogue |
| **TTS** | Text-to-Speech technology for generating voice acting |
| **BGM** | Background Music |
| **LUFS** | Loudness Units Full Scale - audio loudness measurement standard |
| **JWT** | JSON Web Token - standard for secure authentication |
| **WebSocket** | Bi-directional communication protocol for real-time updates |
| **RBAC** | Role-Based Access Control |
| **API** | Application Programming Interface |
| **JSONB** | Binary JSON - PostgreSQL data type for structured data |
| **CQRS** | Command Query Responsibility Segregation - architectural pattern |
| **Saga Pattern** | Distributed transaction management pattern |
| **Viseme** | Visual representation of a phoneme (lip shape for speech) |
| **Phoneme** | Smallest unit of sound in speech |
| **Crossfade** | Audio transition where one sound fades out while another fades in |
| **Volume Ducking** | Automatically lowering BGM volume when voice is present |
| **LUFS** | Loudness Units Full Scale - broadcast loudness standard |

---

## Appendix B: API Payload Examples

### B.1 Authentication Endpoints

**Login Request:**
```json
POST /api/v1/auth/login
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Login Response:**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expires_in": 3600,
    "token_type": "Bearer",
    "user": {
      "id": "uuid",
      "email": "user@example.com",
      "name": "Wang Fang",
      "role": "TEAM_MEMBER",
      "avatar_url": "https://..."
    }
  }
}
```

**Token Refresh:**
```json
POST /api/v1/auth/refresh
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

---

### B.2 Script Generation

**LLM Script Generation Request:**
```json
POST /api/v1/scripts/generate
{
  "project_id": "uuid",
  "prompt": "A romantic comedy about two high school students who meet in the library",
  "tone": "light_hearted",
  "style": "slice_of_life",
  "target_length": "feature",
  "estimated_duration_minutes": 90,
  "language": "zh-CN",
  "llm_config_id": "uuid"
}
```

**Generation Status Poll:**
```json
GET /api/v1/scripts/generate/{job_id}/status

Response:
{
  "success": true,
  "data": {
    "job_id": "uuid",
    "status": "COMPLETED",
    "progress": 1.0,
    "script_id": "uuid",
    "scenes_generated": 45,
    "characters_identified": 8
  }
}
```

---

### B.3 Material Generation

**Batch Image Generation:**
```json
POST /api/v1/generation/images
{
  "project_id": "uuid",
  "panel_ids": ["uuid1", "uuid2", "uuid3"],
  "batch_size": 4,
  "image_config_id": "uuid",
  "style_preset": "anime_standard_v2",
  "aspect_ratio": "16:9",
  "resolution": "1920x1080",
  "negative_prompt": "blurry, low quality, distorted",
  "cfg_scale": 7.5,
  "steps": 30
}
```

**TTS Audio Generation:**
```json
POST /api/v1/generation/audio
{
  "project_id": "uuid",
  "requests": [
    {
      "panel_id": "uuid",
      "text": "你怎么会在这里？",
      "voice_id": "zh-CN-XiaoxiaoNeural",
      "language": "zh-CN",
      "speed": 1.0,
      "pitch": 0,
      "emotion": "surprised",
      "tts_config_id": "uuid"
    }
  ]
}
```

**Video Generation (Lip-Sync):**
```json
POST /api/v1/generation/video
{
  "project_id": "uuid",
  "panel_id": "uuid",
  "image_id": "uuid",
  "audio_id": "uuid",
  "video_config_id": "uuid",
  "model_provider": "heygen_v2",
  "fps": 30,
  "resolution": "1920x1080",
  "lip_sync_accuracy": "high",
  "background_motion": "subtle",
  "output_format": "mp4",
  "codec": "h264"
}
```

---

### B.4 Audit Submission

**First Audit Submission:**
```json
POST /api/v1/audits/first
{
  "chapter_id": "uuid",
  "status": "APPROVED",
  "approved_panels": [1, 2, 3, 4, 5, 6, 7, 8],
  "rejected_panels": [],
  "selections": {
    "uuid1": {"image_id": "uuid", "audio_id": "uuid"},
    "uuid2": {"image_id": "uuid", "audio_id": "uuid"}
  },
  "comments": "All assets look good. Character consistency is excellent.",
  "time_spent_minutes": 25
}
```

**Second Audit Submission (with Rejection):**
```json
POST /api/v1/audits/second
{
  "chapter_id": "uuid",
  "decision": "REJECTED",
  "rating": 3,
  "feedback": "Overall quality is good, but there are lip-sync issues in panels 5-7. Please regenerate video for these panels.",
  "rejection_category": "LIP_SYNC_ISSUES",
  "return_to_step": 6,
  "requires_re_audit": true,
  "timestamped_comments": [
    {
      "timestamp_sec": 12.5,
      "comment": "Mouth movement doesn't match 'ni hao' sound"
    },
    {
      "timestamp_sec": 15.2,
      "comment": "Audio cuts off early"
    }
  ],
  "time_spent_minutes": 18
}
```

---

### B.5 WebSocket Messages

**Progress Update Stream:**
```json
// Initial queue notification
{
  "type": "PROGRESS_UPDATE",
  "payload": {
    "jobId": "uuid",
    "jobType": "IMAGE_GENERATION",
    "status": "QUEUED",
    "progress": 0.0,
    "queue_position": 3,
    "estimated_wait_seconds": 45
  }
}

// Processing started
{
  "type": "PROGRESS_UPDATE",
  "payload": {
    "jobId": "uuid",
    "jobType": "IMAGE_GENERATION",
    "status": "PROCESSING",
    "progress": 0.25,
    "currentStep": "Sending to provider...",
    "totalSteps": 4,
    "completedSteps": 1
  }
}

// Partial results
{
  "type": "PROGRESS_UPDATE",
  "payload": {
    "jobId": "uuid",
    "jobType": "IMAGE_GENERATION",
    "status": "PROCESSING",
    "progress": 0.5,
    "currentStep": "Generating image 2 of 4...",
    "totalSteps": 4,
    "completedSteps": 2,
    "data": {
      "completed_images": [
        {"panel_id": "uuid1", "image_id": "uuid", "thumbnail_url": "https://..."}
      ]
    }
  }
}

// Completion
{
  "type": "TASK_COMPLETE",
  "payload": {
    "jobId": "uuid",
    "jobType": "IMAGE_GENERATION",
    "status": "COMPLETED",
    "result": {
      "generated_items": [
        {"panel_id": "uuid1", "images": [{"id": "uuid", "url": "https://...", "thumbnail": "https://..."}]}
      ],
      "metadata": {
        "generation_time_sec": 45.2,
        "provider": "stability_ai",
        "total_cost_credits": 8
      }
    }
  }
}
```

---

### B.6 Export Request

**Single Chapter Export:**
```json
POST /api/v1/exports/chapter
{
  "chapter_id": "uuid",
  "format": "MP4_H264",
  "preset": "WEB_STANDARD",
  "resolution": "1920x1080",
  "include_subtitles": true,
  "subtitle_format": "BURNED_IN",
  "include_chapter_markers": true,
  "notify_on_complete": true
}
```

**Batch Export Request:**
```json
POST /api/v1/exports/batch
{
  "project_id": "uuid",
  "exports": [
    {
      "chapter_id": "uuid1",
      "format": "MP4_H264",
      "preset": "WEB_STANDARD"
    },
    {
      "chapter_id": "uuid2",
      "format": "MP4_H264",
      "preset": "WEB_STANDARD"
    },
    {
      "chapter_id": "uuid1",
      "format": "WEBM_VP9",
      "preset": "MOBILE"
    }
  ],
  "create_archive": true,
  "archive_format": "ZIP",
  "notify_on_complete": true
}
```

---

## Appendix C: UI Wireframe Diagrams

### C.1 Team Member Dashboard - Task Pipeline View

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│  AI Manga Production System          [Projects] [Help] [Notifications] [Profile]│
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  CURRENT TASK                                                                   │
│  ┌───────────────────────────────────────────────────────────────────────────┐ │
│  │  Project: 魔法学院 (Magic Academy)    Chapter 5: The Discovery           │ │
│  │                                                                           │ │
│  │  Pipeline Progress:                                                       │ │
│  │  ┌─────┐    ┌─────┐    ┌─────┐    ┌─────┐    ┌─────┐    ┌─────┐         │ │
│  │  │  1  │───>│  2  │───>│  3  │───>│  4  │───>│  5  │    │  6  │         │ │
│  │  │ ✓   │    │ ✓   │    │ ✓   │    │ ✓   │    │ >   │    │ ○   │         │ │
│  │  │Script│    │Refine│    │Chapter│    │Story │    │Material│  │Video │         │ │
│  │  └─────┘    └─────┘    └─────┘    └─────┘    └─────┘    └─────┘         │ │
│  │                                              │                            │ │
│  │                                      [CURRENT STEP]                       │ │
│  │                                                                           │ │
│  │  ┌─────────────────────────────────────────────────────────────────────┐ │ │
│  │  │  Step 5: Material Generation                                        │ │ │
│  │  │                                                                     │ │ │
│  │  │  Status: In Progress (45% complete)                                 │ │ │
│  │  │  Estimated time remaining: 2 minutes                                │ │ │
│  │  │                                                                     │ │ │
│  │  │  ┌──────────────────────────────────────────────────────────────┐  │ │ │
│  │  │  │ Panel 1  │ Panel 2  │ Panel 3  │ Panel 4  │ Panel 5 │ ...   │  │ │ │
│  │  │  │  ✓ Done  │  ✓ Done  │  ⏳ Gen  │  ⏳ Gen  │  ○ Wait │       │  │ │ │
│  │  │  │ [View]   │ [View]   │ [View]   │ [View]   │ [View]  │       │  │ │ │
│  │  │  └──────────────────────────────────────────────────────────────┘  │ │ │
│  │  │                                                                     │ │ │
│  │  │  [Refresh Status]  [View Instructions]  [Report Issue]             │ │ │
│  │  └─────────────────────────────────────────────────────────────────────┘ │ │
│  └───────────────────────────────────────────────────────────────────────────┘ │
│                                                                                 │
│  ┌─────────────────────────────┐   ┌─────────────────────────────────────────┐ │
│  │  UPCOMING TASKS (3)         │   │  COMPLETED THIS WEEK                    │ │
│  │                             │   │                                         │ │
│  │  ▶ Ch.6 - Storyboard        │   │  ✓ Ch.3 - Published      Mar 15        │ │
│  │    Due: Tomorrow            │   │  ✓ Ch.4 - First Audit    Mar 17        │ │
│  │                             │   │  ✓ Ch.2 - Published      Mar 14        │ │
│  │  ▶ Ch.7 - Video Gen         │   │                                         │ │
│  │    Due: Mar 20              │   │  [View All Completed →]                 │ │
│  │                             │   │                                         │ │
│  │  ▶ Ch.8 - First Audit       │   │                                         │ │
│  │    Due: Mar 22              │   │                                         │ │
│  └─────────────────────────────┘   └─────────────────────────────────────────┘ │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

### C.2 First Audit Interface - Card Draw Selection

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│  ← Back to Task    Chapter 5: The Discovery    Step 5/8    [Submit for Review] │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  FIRST AUDIT - Material Selection                                               │
│  ┌───────────────────────────────────────────────────────────────────────────┐ │
│  │  Progress: 6/8 panels selected                                            │ │
│  │  ████████████████████░░░░░░░░ 75%                                         │ │
│  └───────────────────────────────────────────────────────────────────────────┘ │
│                                                                                 │
│  ┌───────────────────────────────────────────────────────────────────────────┐ │
│  │  PANEL 3 of 8    Dialogue: "你怎么会在这里？"                              │ │
│  │                                                                           │ │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │ │
│  │  │          │ │          │ │          │ │          │ │          │       │ │
│  │  │  Image 1 │ │  Image 2 │ │  Image 3 │ │  Image 4 │ │ + Generate│       │ │
│  │  │          │ │          │ │          │ │          │ │  More     │       │ │
│  │  │          │ │          │ │          │ │          │ │          │       │ │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘       │ │
│  │       ○            ●            ○            ○          [+]              │ │
│  │                                                                           │ │
│  │  Selected: Image 2    [Preview Full Size]                                 │ │
│  │                                                                           │ │
│  │  ┌─────────────────────────────────────────────────────────────────────┐ │ │
│  │  │ Audio Options                                                        │ │ │
│  │  │ ┌────────────────────────────────────────────────────────────────┐  │ │ │
│  │  │ │ ▶ Xiaoxiao (Female, Young)   ████░░░░░░  [Waveform]  [Select] │  │ │ │
│  │  │ └────────────────────────────────────────────────────────────────┘  │ │ │
│  │  │ ┌────────────────────────────────────────────────────────────────┐  │ │ │
│  │  │ │ ▶ Yuning (Female, Calm)    ███░░░░░░░░  [Waveform]  [Select]  │  │ │ │
│  │  │ └────────────────────────────────────────────────────────────────┘  │ │ │
│  │  └─────────────────────────────────────────────────────────────────────┘ │ │
│  │                                                                           │ │
│  │  [← Previous Panel]                    [Next Panel →]  [Skip for Now]    │ │
│  └───────────────────────────────────────────────────────────────────────────┘ │
│                                                                                 │
│  Panel Thumbnails:                                                              │
│  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐              │
│  │  1  │ │  2  │ │  3  │ │  4  │ │  5  │ │  6  │ │  7  │ │  8  │              │
│  │  ✓  │ │  ✓  │ │  ●  │ │  ✓  │ │  ✓  │ │  ✓  │ │  ○  │ │  ○  │              │
│  └─────┘ └─────┘ └─────┘ └─────┘ └─────┘ └─────┘ └─────┘ └─────┘              │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

### C.3 Team Lead Dashboard - Review Queue

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│  AI Manga Production System    [Dashboard] [Projects] [Team] [Reports] [Settings]│
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  PENDING REVIEWS                                                                │
│  ┌───────────────────────────────────────────────────────────────────────────┐ │
│  │  ⚠️ 3 items awaiting your review                                          │ │
│  └───────────────────────────────────────────────────────────────────────────┘ │
│                                                                                 │
│  ┌───────────────────────────────────────────────────────────────────────────┐ │
│  │  🔴 HIGH PRIORITY                                                          │ │
│  │  ┌─────────────────────────────────────────────────────────────────────┐ │ │
│  │  │ Chapter 7: The Battle   魔法学院                                    │ │ │
│  │  │                                                                     │ │ │
│  │  │  Type: Second Audit (Final Approval)                                │ │ │
│  │  │  Submitted by: Wang Fang    │    Submitted: 2 hours ago             │ │ │
│  │  │                                                                     │ │ │
│  │  │  First Audit Result: Approved (Rating: 4.5/5)                       │ │ │
│  │  │  Comments: "Excellent lip-sync quality, minor BGM adjustment needed"│ │ │
│  │  │                                                                     │ │ │
│  │  │  ┌───────────────────────────────────────────────────────────────┐ │ │ │
│  │  │  │ ▶ Preview Video (2:45)                    [Full Screen]       │ │ │ │
│  │  │  └───────────────────────────────────────────────────────────────┘ │ │ │
│  │  │                                                                     │ │ │
│  │  │  [Add Comment]  [Request Minor Edit]  [Reject]  [✓ Approve]        │ │ │
│  │  └─────────────────────────────────────────────────────────────────────┘ │ │
│  └───────────────────────────────────────────────────────────────────────────┘ │
│                                                                                 │
│  ┌───────────────────────────────────────────────────────────────────────────┐ │
│  │  🟡 NORMAL PRIORITY                                                        │ │
│  │  ┌─────────────────────────────────────────────────────────────────────┐ │ │
│  │  │ Chapter 5: The Discovery   魔法学院                                 │ │ │
│  │  │                                                                     │ │ │
│  │  │  Type: First Audit Review                                           │ │ │
│  │  │  Submitted by: Li Ming    │    Submitted: 5 hours ago               │ │ │
│  │  │                                                                     │ │ │
│  │  │  Status: 8/8 panels selected, awaiting your approval                │ │ │
│  │  │                                                                     │ │ │
│  │  │  [Review Materials]  [Auto-Approve if All Selected]                 │ │ │
│  │  └─────────────────────────────────────────────────────────────────────┘ │ │
│  └───────────────────────────────────────────────────────────────────────────┘ │
│                                                                                 │
│  ┌───────────────────────────────────────────────────────────────────────────┐ │
│  │  🟢 MINOR EDITS (No Re-Audit Required)                                    │ │
│  │  ┌─────────────────────────────────────────────────────────────────────┐ │ │
│  │  │ Chapter 3: Unexpected Meeting   魔法学院                            │ │ │
│  │  │                                                                     │ │ │
│  │  │  Type: Minor Edit Request                                           │ │ │
│  │  │  Issue: Subtitle typo in panel 4                                    │ │ │
│  │  │                                                                     │ │ │
│  │  │  [Review Edit]  [Approve Change]                                    │ │ │
│  │  └─────────────────────────────────────────────────────────────────────┘ │ │
│  └───────────────────────────────────────────────────────────────────────────┘ │
│                                                                                 │
│  RECENT APPROVALS                                                               │
│  ✓ Chapter 2 - Approved Mar 18    ✓ Chapter 1 - Published Mar 17               │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

### C.4 Admin Dashboard - System Overview

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│  ADMIN DASHBOARD                              [User Mgmt] [Configs] [Logs] [Settings]│
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐│
│  │  System Health  │  │   API Usage     │  │  Active Users   │  │  Storage    ││
│  │                 │  │                 │  │                 │  │             ││
│  │     ● 99.8%     │  │    78% used     │  │      24         │  │  456/1000GB ││
│  │    Uptime       │  │  of 10K calls   │  │    online       │  │    (45.6%)  ││
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  └─────────────┘│
│                                                                                 │
│  ┌───────────────────────────────────────────────────────────────────────────┐ │
│  │                        PROJECTS OVERVIEW                                   │ │
│  │  ┌──────────┬─────────┬──────────┬─────────┬──────────┬──────────────┐   │ │
│  │  │ Project  │ Status  │ Members  │ Progress │ API Calls│ Actions      │   │ │
│  │  ├──────────┼─────────┼──────────┼─────────┼──────────┼──────────────┤   │ │
│  │  │ 魔法学院  │ ● Active│    8     │   75%   │  4,521   │ [View][Edit] │   │ │
│  │  │ action_01│ ● Active│    5     │   30%   │  1,234   │ [View][Edit] │   │ │
│  │  │ romance_v│ ● Active│   12     │   55%   │  2,890   │ [View][Edit] │   │ │
│  │  │ archive_0│ ○ Arch  │    3     │  100%   │    500   │ [View][Edit] │   │ │
│  │  └──────────┴─────────┴──────────┴─────────┴──────────┴──────────────┘   │ │
│  │                                                                           │ │
│  │  [+ Create New Project]  [Export All Data]                                │ │
│  └───────────────────────────────────────────────────────────────────────────┘ │
│                                                                                 │
│  ┌──────────────────────────────┐  ┌─────────────────────────────────────────┐ │
│  │   MODEL PROVIDER STATUS      │  │   RECENT SYSTEM AUDIT LOGS              │ │
│  │                              │  │                                         │ │
│  │  LLM:                        │  │  [10:32] Admin created project          │ │
│  │  ● OpenAI GPT-4     Healthy  │  │  [10:28] Wang Fang approved Ch.5        │ │
│  │  ● Claude-3         Healthy  │  │  [10:15] API key rotated (Image)        │ │
│  │                              │  │  [09:45] Li Ming login                  │ │
│  │  Image:                      │  │  [09:30] System: Backup completed       │ │
│  │  ● Stability AI     Healthy  │  │  [09:00] System: Daily report generated │ │
│  │  ○ Midjourney       Degraded │  │                                         │ │
│  │                              │  │  [View All Logs →]                      │ │
│  │  Video:                      │  │                                         │ │
│  │  ● HeyGen           Healthy  │  │                                         │ │
│  │                              │  │                                         │ │
│  │  TTS:                        │  │                                         │ │
│  │  ● Azure TTS        Healthy  │  │                                         │ │
│  │  ● ElevenLabs       Healthy  │  │                                         │ │
│  └──────────────────────────────┘  └─────────────────────────────────────────┘ │
│                                                                                 │
│  ┌───────────────────────────────────────────────────────────────────────────┐ │
│  │   ALERTS & WARNINGS                                                        │ │
│  │  ⚠️ Midjourney API experiencing higher than normal latency (avg 8s)       │ │
│  │  ℹ️  Weekly backup scheduled for 02:00 AM tonight                          │ │
│  └───────────────────────────────────────────────────────────────────────────┘ │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## Appendix D: Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-03-01 | Product Manager | Initial draft |
| 1.1 | 2026-03-01 | Product Manager | Added storage quotas, WebSocket specs, AI fallback logic, task assignment workflow, export requirements, API examples, and wireframe diagrams |

---

## Appendix E: Open Questions

| Question | Status | Owner | Priority |
|----------|--------|-------|----------|
| Specific AI model providers to support at launch | Pending | Technical Lead | P0 |
| Pricing/quota model for API usage | Pending | Product | P0 |
| Accessibility requirements (WCAG level) | Pending | Design | P1 |
| Supported languages beyond Chinese | Pending | Product | P1 |
| CDN provider selection | Pending | Infrastructure | P1 |
| Mobile app roadmap | Pending | Product | P2 |

---

**END OF PRD**
