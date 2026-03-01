"""
ARQ Worker and Task Definitions

Updated to use AIService for real AI provider integration.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from arq.worker import Worker
from app.database import SessionLocal
from app.models.generation_job import GenerationJob, JobStatus
from app.models.model_provider import ModelProvider
from app.services.websocket import manager, WebSocketMessage
from app.services.ai_service import AIService
from app.services.storage import MinIOStorage

logger = logging.getLogger(__name__)


class WorkerSettings:
    """ARQ Worker Configuration"""

    redis_host = "localhost"
    redis_port = 6379
    redis_db = 0

    # Job execution settings
    job_timeout = 600  # 10 minutes max per job
    max_tries = 3  # Retry up to 3 times
    retry_delay = 5  # 5 seconds between retries

    # Functions that can be executed by workers
    functions = [
        "app.services.worker.generate_images_task",
        "app.services.worker.generate_audio_task",
        "app.services.worker.generate_video_task",
        "app.services.worker.compose_chapter_task",
        "app.services.worker.export_video_task",
        "app.services.worker.llm_generate_script_task",
        "app.services.worker.generate_storyboard_task",
        "app.services.worker.recommend_bgm_task",
        "app.services.worker.cleanup_old_jobs",
        "app.services.worker.health_check_providers",
    ]

    # Lifecycle hooks
    async def on_start(self, worker: Worker):
        logger.info("Worker started")

    async def on_shutdown(self, worker: Worker):
        logger.info("Worker shutting down")

    async def on_job_start(self, ctx: Dict, job_id: str, job_name: str):
        logger.info(f"Job {job_id} ({job_name}) started")

    async def on_job_end(self, ctx: Dict, job_id: str, job_name: str, result: Any, duration: float):
        logger.info(f"Job {job_id} ({job_name}) completed in {duration:.2f}s")


def get_db() -> Session:
    """Get database session"""
    return SessionLocal()


async def update_job_status(
    db: Session,
    job_id: int,
    status: JobStatus,
    progress: int = None,
    result_data: dict = None,
    error_message: str = None,
):
    """Update job status in database"""
    job = db.query(GenerationJob).filter(GenerationJob.id == job_id).first()
    if not job:
        logger.error(f"Job {job_id} not found")
        return

    job.status = status.value
    if progress is not None:
        job.progress = progress
    if result_data:
        job.result_data = result_data
    if error_message:
        job.error_message = error_message
    if status == JobStatus.RUNNING:
        job.started_at = datetime.utcnow()
    elif status in [JobStatus.COMPLETED, JobStatus.FAILED]:
        job.completed_at = datetime.utcnow()

    db.commit()
    return job


async def notify_progress(job_id: int, progress: int, status: str, message: str = None):
    """Send progress update via WebSocket"""
    await manager.send_personal(
        job_id,  # Using job_id as user_id for project-based notifications
        WebSocketMessage.progress_update(job_id, progress, status, message)
    )


async def notify_complete(job_id: int, result: dict = None):
    """Send task complete notification via WebSocket"""
    await manager.send_personal(
        job_id,
        WebSocketMessage.task_complete(job_id, result)
    )


async def notify_error(job_id: int, error: str):
    """Send task error notification via WebSocket"""
    await manager.send_personal(
        job_id,
        WebSocketMessage.task_error(job_id, error)
    )


# ============================================
# Task Implementations
# ============================================

async def generate_images_task(ctx: Dict, job_id: int, storyboard_id: int, count: int = 3):
    """
    Generate images for a storyboard panel

    Args:
        job_id: Generation job ID
        storyboard_id: Storyboard panel ID
        count: Number of images to generate (抽卡制)
    """
    db = get_db()
    try:
        job = db.query(GenerationJob).filter(GenerationJob.id == job_id).first()
        if not job:
            return

        # Update status to running
        await update_job_status(db, job_id, JobStatus.RUNNING, progress=10)
        await notify_progress(job_id, 10, "running", "Starting image generation...")

        # Get storyboard for prompt
        from app.models.storyboard import Storyboard
        storyboard = db.query(Storyboard).filter(Storyboard.id == storyboard_id).first()

        if not storyboard:
            raise Exception("Storyboard not found")

        # Use AIService for image generation
        ai_service = AIService(db)

        # Build prompt from storyboard
        prompt_parts = []
        if storyboard.visual_description:
            prompt_parts.append(storyboard.visual_description)
        if storyboard.camera_direction:
            prompt_parts.append(f"Camera: {storyboard.camera_direction}")
        if storyboard.emotion:
            prompt_parts.append(f"Mood: {storyboard.emotion}")

        prompt = ", ".join(prompt_parts) if prompt_parts else "Generate scene image"

        await notify_progress(job_id, 30, "running", f"Generating {count} images using AI...")

        # Generate images using AIService
        result = await ai_service.generate_images(
            prompt=prompt,
            count=count,
            width=1024,
            height=1024,
            save_to_storage=True,
        )

        if not result.success:
            raise Exception(f"AI generation failed: {result.error}")

        generated_images = result.data or []

        # Update job status
        await update_job_status(
            db,
            job_id,
            JobStatus.COMPLETED,
            progress=100,
            result_data={"images": generated_images}
        )

        await notify_progress(job_id, 100, "completed", "Image generation completed")
        await notify_complete(job_id, {"images": generated_images})

    except Exception as e:
        logger.error(f"Image generation failed: {e}")
        await update_job_status(db, job_id, JobStatus.FAILED, error_message=str(e))
        await notify_error(job_id, str(e))
    finally:
        db.close()


async def generate_audio_task(ctx: Dict, job_id: int, storyboard_id: int, voice_id: str = None):
    """
    Generate audio (TTS) for a storyboard panel

    Args:
        job_id: Generation job ID
        storyboard_id: Storyboard panel ID
        voice_id: Voice ID for TTS
    """
    db = get_db()
    try:
        await update_job_status(db, job_id, JobStatus.RUNNING, progress=10)
        await notify_progress(job_id, 10, "running", "Starting audio generation...")

        # Get storyboard dialogue
        from app.models.storyboard import Storyboard
        storyboard = db.query(Storyboard).filter(Storyboard.id == storyboard_id).first()

        if not storyboard or not storyboard.dialogue:
            raise Exception("Storyboard not found or no dialogue")

        # Use AIService for TTS
        ai_service = AIService(db)

        await notify_progress(job_id, 50, "running", "Synthesizing voice...")

        # Generate audio using AIService
        result = await ai_service.synthesize_audio(
            text=storyboard.dialogue,
            voice_id=voice_id or "alloy",
            save_to_storage=True,
        )

        if not result.success:
            raise Exception(f"TTS generation failed: {result.error}")

        audio_data = result.data or {}

        await update_job_status(
            db,
            job_id,
            JobStatus.COMPLETED,
            progress=100,
            result_data={"audio": audio_data}
        )

        await notify_progress(job_id, 100, "completed", "Audio generation completed")
        await notify_complete(job_id, {"audio": audio_data})

    except Exception as e:
        logger.error(f"Audio generation failed: {e}")
        await update_job_status(db, job_id, JobStatus.FAILED, error_message=str(e))
        await notify_error(job_id, str(e))
    finally:
        db.close()


async def generate_video_task(ctx: Dict, job_id: int, storyboard_id: int):
    """
    Generate video with lip-sync for a storyboard panel

    Args:
        job_id: Generation job ID
        storyboard_id: Storyboard panel ID
    """
    db = get_db()
    try:
        await update_job_status(db, job_id, JobStatus.RUNNING, progress=10)
        await notify_progress(job_id, 10, "running", "Starting video generation...")

        # Get storyboard for image URL
        from app.models.storyboard import Storyboard
        from app.models.asset import Asset

        storyboard = db.query(Storyboard).filter(Storyboard.id == storyboard_id).first()
        if not storyboard:
            raise Exception("Storyboard not found")

        # Get generated image for this storyboard
        image_asset = db.query(Asset).filter(
            Asset.storyboard_id == storyboard_id,
            Asset.type == "image"
        ).first()

        if not image_asset or not image_asset.url:
            raise Exception("No source image found for storyboard")

        # Get generated audio for lip-sync
        audio_asset = db.query(Asset).filter(
            Asset.storyboard_id == storyboard_id,
            Asset.type == "audio"
        ).first()

        # Use AIService for video generation
        ai_service = AIService(db)

        await notify_progress(job_id, 40, "running", "Generating video with lip-sync...")

        # Generate video using AIService
        result = await ai_service.generate_video(
            image_url=image_asset.url,
            audio_url=audio_asset.url if audio_asset else None,
            duration=storyboard.duration_seconds or 5.0,
            lip_sync=True,
            save_to_storage=True,
        )

        if not result.success:
            raise Exception(f"Video generation failed: {result.error}")

        video_data = result.data or {}

        await update_job_status(
            db,
            job_id,
            JobStatus.COMPLETED,
            progress=100,
            result_data={"video": video_data}
        )

        await notify_progress(job_id, 100, "completed", "Video generation completed")
        await notify_complete(job_id, {"video": video_data})

    except Exception as e:
        logger.error(f"Video generation failed: {e}")
        await update_job_status(db, job_id, JobStatus.FAILED, error_message=str(e))
        await notify_error(job_id, str(e))
    finally:
        db.close()


async def compose_chapter_task(ctx: Dict, job_id: int, chapter_id: int):
    """
    Compose chapter video from storyboards

    Args:
        job_id: Generation job ID
        chapter_id: Chapter ID
    """
    db = get_db()
    try:
        await update_job_status(db, job_id, JobStatus.RUNNING, progress=10)
        await notify_progress(job_id, 10, "running", "Starting chapter composition...")

        # Mock composition process
        await notify_progress(job_id, 50, "running", "Compositing video, audio, subtitles...")
        await asyncio.sleep(15)

        video_data = {
            "url": f"/assets/generated/chapter_{chapter_id}.mp4",
            "duration": 60.0,
        }

        await update_job_status(
            db,
            job_id,
            JobStatus.COMPLETED,
            progress=100,
            result_data={"video": video_data}
        )

        await notify_progress(job_id, 100, "completed", "Chapter composition completed")
        await notify_complete(job_id, {"video": video_data})

    except Exception as e:
        logger.error(f"Chapter composition failed: {e}")
        await update_job_status(db, job_id, JobStatus.FAILED, error_message=str(e))
        await notify_error(job_id, str(e))
    finally:
        db.close()


async def export_video_task(ctx: Dict, job_id: int, project_id: int, format: str = "mp4"):
    """
    Export final video

    Args:
        job_id: Generation job ID
        project_id: Project ID
        format: Export format (mp4, mov, webm)
    """
    db = get_db()
    try:
        await update_job_status(db, job_id, JobStatus.RUNNING, progress=10)
        await notify_progress(job_id, 10, "running", f"Starting {format} export...")

        # Mock export process
        await notify_progress(job_id, 50, "running", "Rendering video...")
        await asyncio.sleep(20)

        video_data = {
            "url": f"/assets/exports/project_{project_id}.{format}",
            "format": format,
            "file_size": 100 * 1024 * 1024,  # 100MB mock
        }

        await update_job_status(
            db,
            job_id,
            JobStatus.COMPLETED,
            progress=100,
            result_data={"video": video_data}
        )

        await notify_progress(job_id, 100, "completed", f"{format} export completed")
        await notify_complete(job_id, {"video": video_data})

    except Exception as e:
        logger.error(f"Video export failed: {e}")
        await update_job_status(db, job_id, JobStatus.FAILED, error_message=str(e))
        await notify_error(job_id, str(e))
    finally:
        db.close()


async def llm_generate_script_task(ctx: Dict, job_id: int, prompt: str, project_id: int):
    """
    Generate script using LLM

    Args:
        job_id: Generation job ID
        prompt: Script generation prompt
        project_id: Project ID
    """
    db = get_db()
    try:
        await update_job_status(db, job_id, JobStatus.RUNNING, progress=10)
        await notify_progress(job_id, 10, "running", "Initializing LLM...")

        # Use AIService for LLM generation
        ai_service = AIService(db)

        await notify_progress(job_id, 50, "running", "Generating script...")

        # Generate script using AIService
        result = await ai_service.generate_text(
            prompt=prompt,
            system_prompt="你是一位专业的编剧，擅长创作引人入胜的漫剧剧本。请根据用户提供的主题创作剧本，包含场景描述、角色对话和镜头指示。",
            max_tokens=4096,
            temperature=0.7,
        )

        if not result.success:
            raise Exception(f"LLM generation failed: {result.error}")

        script_content = result.data or ""

        await update_job_status(
            db,
            job_id,
            JobStatus.COMPLETED,
            progress=100,
            result_data={"content": script_content}
        )

        await notify_progress(job_id, 100, "completed", "Script generation completed")
        await notify_complete(job_id, {"content": script_content})

    except Exception as e:
        logger.error(f"Script generation failed: {e}")
        await update_job_status(db, job_id, JobStatus.FAILED, error_message=str(e))
        await notify_error(job_id, str(e))
    finally:
        db.close()


async def generate_storyboard_task(ctx: Dict, job_id: int, chapter_id: int):
    """
    Generate storyboards from chapter content

    Args:
        job_id: Generation job ID
        chapter_id: Chapter ID
    """
    db = get_db()
    try:
        await update_job_status(db, job_id, JobStatus.RUNNING, progress=10)
        await notify_progress(job_id, 10, "running", "Generating storyboards...")

        # Get chapter content
        from app.models.chapter import Chapter
        chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()

        if not chapter:
            raise Exception("Chapter not found")

        # Use AIService for storyboard generation
        ai_service = AIService(db)

        # Build prompt for storyboard generation
        prompt = f"""请根据以下章节内容生成分镜脚本：

章节标题：{chapter.title}
章节内容：{chapter.content or ''}

要求：
1. 每个分镜包含画面描述、镜头语言、角色台词
2. 分镜数量适合章节内容（通常 5-10 个）
3. 指定每个分镜的情绪基调和时长

请以 JSON 格式返回分镜列表。"""

        await notify_progress(job_id, 40, "running", "AI generating storyboards...")

        result = await ai_service.generate_text(
            prompt=prompt,
            system_prompt="你是一位专业的分镜师，擅长将剧本内容转化为详细的分镜脚本。请输出结构化的分镜数据，包含 order、visual_description、camera_direction、dialogue、emotion、duration_seconds 等字段。",
            max_tokens=4096,
        )

        if not result.success:
            raise Exception(f"Storyboard generation failed: {result.error}")

        # Parse AI response (expect JSON)
        import json
        try:
            storyboards = json.loads(result.data)
            if isinstance(storyboards, list):
                storyboards = [{"order": i + 1, **sb} for i, sb in enumerate(storyboards)]
            else:
                storyboards = [storyboards]
        except json.JSONDecodeError:
            # Fallback: create simple storyboard from response
            storyboards = [
                {
                    "order": 1,
                    "visual_description": result.data[:500],
                    "dialogue": "",
                    "emotion": "neutral",
                    "duration_seconds": 5,
                }
            ]

        await update_job_status(
            db,
            job_id,
            JobStatus.COMPLETED,
            progress=100,
            result_data={"storyboards": storyboards}
        )

        await notify_progress(job_id, 100, "completed", "Storyboard generation completed")
        await notify_complete(job_id, {"storyboards": storyboards})

    except Exception as e:
        logger.error(f"Storyboard generation failed: {e}")
        await update_job_status(db, job_id, JobStatus.FAILED, error_message=str(e))
        await notify_error(job_id, str(e))
    finally:
        db.close()


async def recommend_bgm_task(ctx: Dict, job_id: int, project_id: int, emotions: list = None):
    """
    Recommend BGM based on emotions

    Args:
        job_id: Generation job ID
        project_id: Project ID
        emotions: List of emotions
    """
    db = get_db()
    try:
        await update_job_status(db, job_id, JobStatus.RUNNING, progress=10)
        await notify_progress(job_id, 10, "running", "Analyzing emotions...")

        # Use AIService for BGM recommendation
        ai_service = AIService(db)

        emotions_str = ", ".join(emotions) if emotions else "neutral"

        await notify_progress(job_id, 40, "running", "Recommending BGM...")

        result = await ai_service.recommend_bgm(
            mood=emotions_str,
            emotion=emotions[0] if emotions else "neutral",
            duration=60.0,
        )

        if not result.success:
            # Use mock data if provider fails
            bgm_recommendations = [
                {"title": f"{emotions_str} Background 1", "mood": emotions_str, "url": "/bgm/default1.mp3"},
                {"title": f"{emotions_str} Background 2", "mood": emotions_str, "url": "/bgm/default2.mp3"},
            ]
        else:
            bgm_recommendations = result.data or []

        await update_job_status(
            db,
            job_id,
            JobStatus.COMPLETED,
            progress=100,
            result_data={"bgm_recommendations": bgm_recommendations}
        )

        await notify_progress(job_id, 100, "completed", "BGM recommendation completed")
        await notify_complete(job_id, {"bgm_recommendations": bgm_recommendations})

    except Exception as e:
        logger.error(f"BGM recommendation failed: {e}")
        await update_job_status(db, job_id, JobStatus.FAILED, error_message=str(e))
        await notify_error(job_id, str(e))
    finally:
        db.close()


# ============================================
# Scheduled Tasks
# ============================================

async def cleanup_old_jobs(ctx: Dict):
    """Clean up old completed jobs (daily)"""
    db = get_db()
    try:
        cutoff = datetime.utcnow() - timedelta(days=30)
        deleted = db.query(GenerationJob).filter(
            GenerationJob.completed_at < cutoff
        ).delete()
        db.commit()
        logger.info(f"Cleaned up {deleted} old jobs")
    except Exception as e:
        logger.error(f"Cleanup failed: {e}")
    finally:
        db.close()


async def health_check_providers(ctx: Dict):
    """Health check for AI providers (every 5 minutes)"""
    db = get_db()
    try:
        providers = db.query(ModelProvider).filter(ModelProvider.is_active == True).all()
        for provider in providers:
            # TODO: Implement actual health check
            provider.health_status = "healthy"
            provider.last_health_check = datetime.utcnow()
        db.commit()
        logger.info("Provider health check completed")
    except Exception as e:
        logger.error(f"Health check failed: {e}")
    finally:
        db.close()
