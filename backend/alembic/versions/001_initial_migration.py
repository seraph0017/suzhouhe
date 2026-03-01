"""Initial migration - Create all tables

Revision ID: 001
Revises:
Create Date: 2026-03-01

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('role', sa.Enum('admin', 'team_lead', 'team_member', name='userrole'), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)

    # Projects table
    op.create_table(
        'projects',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.Enum('planning', 'in_progress', 'on_hold', 'completed', 'archived', name='projectstatus'), nullable=True, default='planning'),
        sa.Column('team_lead_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(['team_lead_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_projects_id'), 'projects', ['id'], unique=False)

    # Project members table
    op.create_table(
        'project_members',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.Enum('lead', 'member', 'viewer', name='projectmemberrole'), nullable=True, default='member'),
        sa.Column('joined_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('project_id', 'user_id', name='unique_project_user'),
    )
    op.create_index(op.f('ix_project_members_id'), 'project_members', ['id'], unique=False)
    op.create_index(op.f('ix_project_members_project_id'), 'project_members', ['project_id'], unique=False)
    op.create_index(op.f('ix_project_members_user_id'), 'project_members', ['user_id'], unique=False)

    # Model providers table
    op.create_table(
        'model_providers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('provider_type', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('display_name', sa.String(length=200), nullable=True),
        sa.Column('api_endpoint', sa.String(length=500), nullable=True),
        sa.Column('api_key', sa.String(length=500), nullable=False),
        sa.Column('config', sa.JSON(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('is_default', sa.Boolean(), nullable=True, default=False),
        sa.Column('last_health_check', sa.DateTime(timezone=True), nullable=True),
        sa.Column('health_status', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_model_providers_id'), 'model_providers', ['id'], unique=False)

    # Scripts table
    op.create_table(
        'scripts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('version', sa.Integer(), nullable=True, default=1),
        sa.Column('status', sa.Enum('draft', 'in_review', 'locked', 'archived', name='scriptstatus'), nullable=True, default='draft'),
        sa.Column('is_locked', sa.Boolean(), nullable=True, default=False),
        sa.Column('locked_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('locked_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(['locked_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_scripts_id'), 'scripts', ['id'], unique=False)

    # Script versions table
    op.create_table(
        'script_versions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('script_id', sa.Integer(), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('change_description', sa.Text(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['script_id'], ['scripts.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_script_versions_id'), 'script_versions', ['id'], unique=False)

    # Chapters table
    op.create_table(
        'chapters',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('script_id', sa.Integer(), nullable=False),
        sa.Column('order', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('status', sa.Enum('draft', 'in_progress', 'in_review', 'completed', 'archived', name='chapterstatus'), nullable=True, default='draft'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(['script_id'], ['scripts.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_chapters_id'), 'chapters', ['id'], unique=False)

    # Storyboards table
    op.create_table(
        'storyboards',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('chapter_id', sa.Integer(), nullable=False),
        sa.Column('order', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=True),
        sa.Column('visual_description', sa.Text(), nullable=False),
        sa.Column('camera_direction', sa.Text(), nullable=True),
        sa.Column('dialogue', sa.Text(), nullable=True),
        sa.Column('duration_seconds', sa.Float(), nullable=True, default=5.0),
        sa.Column('emotion', sa.String(length=50), nullable=True),
        sa.Column('status', sa.Enum('draft', 'in_review', 'locked', 'materials_generated', 'video_generated', 'completed', name='storyboardstatus'), nullable=True, default='draft'),
        sa.Column('is_locked', sa.Boolean(), nullable=True, default=False),
        sa.Column('selected_image_id', sa.Integer(), nullable=True),
        sa.Column('selected_audio_id', sa.Integer(), nullable=True),
        sa.Column('selected_video_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.Column('locked_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['chapter_id'], ['chapters.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_storyboards_id'), 'storyboards', ['id'], unique=False)

    # Assets table
    op.create_table(
        'assets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('storyboard_id', sa.Integer(), nullable=True),
        sa.Column('type', sa.Enum('image', 'audio', 'video', 'document', 'other', name='assettype'), nullable=False),
        sa.Column('status', sa.Enum('pending', 'processing', 'completed', 'failed', 'archived', name='assetstatus'), nullable=True, default='pending'),
        sa.Column('file_path', sa.String(length=500), nullable=False),
        sa.Column('file_name', sa.String(length=255), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=True),
        sa.Column('mime_type', sa.String(length=100), nullable=True),
        sa.Column('url', sa.String(length=500), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('provider', sa.String(length=100), nullable=True),
        sa.Column('model_name', sa.String(length=100), nullable=True),
        sa.Column('generation_params', sa.JSON(), nullable=True),
        sa.Column('duration_seconds', sa.Float(), nullable=True),
        sa.Column('width', sa.Integer(), nullable=True),
        sa.Column('height', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['storyboard_id'], ['storyboards.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_assets_id'), 'assets', ['id'], unique=False)

    # Update storyboards with foreign key to assets
    # (This requires altering the table - done via batch mode for SQLite compatibility)
    with op.batch_alter_table('storyboards', schema=None) as batch_op:
        batch_op.create_foreign_key(
            'fk_storyboards_selected_image',
            'assets', ['selected_image_id'], ['id']
        )
        batch_op.create_foreign_key(
            'fk_storyboards_selected_audio',
            'assets', ['selected_audio_id'], ['id']
        )
        batch_op.create_foreign_key(
            'fk_storyboards_selected_video',
            'assets', ['selected_video_id'], ['id']
        )

    # Reviews table
    op.create_table(
        'reviews',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('review_type', sa.Enum('first_audit', 'second_audit', 'script_review', 'storyboard_review', name='reviewtype'), nullable=False),
        sa.Column('target_type', sa.String(length=50), nullable=False),
        sa.Column('target_id', sa.Integer(), nullable=False),
        sa.Column('reviewer_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.Enum('pending', 'approved', 'rejected', 'changes_requested', name='reviewstatus'), nullable=True, default='pending'),
        sa.Column('feedback', sa.Text(), nullable=True),
        sa.Column('rejection_reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['reviewer_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_reviews_id'), 'reviews', ['id'], unique=False)

    # Audit logs table
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=True),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('entity_type', sa.String(length=50), nullable=False),
        sa.Column('entity_id', sa.Integer(), nullable=True),
        sa.Column('changes', sa.JSON(), nullable=True),
        sa.Column('ip_address', sa.String(length=50), nullable=True),
        sa.Column('user_agent', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_audit_logs_id'), 'audit_logs', ['id'], unique=False)
    op.create_index(op.f('ix_audit_logs_user_id'), 'audit_logs', ['user_id'], unique=False)
    op.create_index(op.f('ix_audit_logs_project_id'), 'audit_logs', ['project_id'], unique=False)

    # Tasks table
    op.create_table(
        'tasks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('chapter_id', sa.Integer(), nullable=True),
        sa.Column('assigned_to', sa.Integer(), nullable=True),
        sa.Column('assigned_by', sa.Integer(), nullable=True),
        sa.Column('task_type', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=True, default='pending'),
        sa.Column('priority', sa.String(length=20), nullable=True, default='normal'),
        sa.Column('due_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(['assigned_by'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['assigned_to'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['chapter_id'], ['chapters.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_tasks_id'), 'tasks', ['id'], unique=False)
    op.create_index(op.f('ix_tasks_assigned_to'), 'tasks', ['assigned_to'], unique=False)
    op.create_index(op.f('ix_tasks_status'), 'tasks', ['status'], unique=False)
    op.create_index(op.f('ix_tasks_project'), 'tasks', ['project_id'], unique=False)

    # Generation jobs table
    op.create_table(
        'generation_jobs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('storyboard_id', sa.Integer(), nullable=True),
        sa.Column('job_type', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=True, default='queued'),
        sa.Column('model_config_id', sa.Integer(), nullable=True),
        sa.Column('request_params', sa.JSON(), nullable=True),
        sa.Column('result_data', sa.JSON(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('progress', sa.Integer(), nullable=True, default=0),
        sa.Column('retry_count', sa.Integer(), nullable=True, default=0),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['model_config_id'], ['model_providers.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['storyboard_id'], ['storyboards.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_generation_jobs_id'), 'generation_jobs', ['id'], unique=False)
    op.create_index(op.f('ix_generation_jobs_status'), 'generation_jobs', ['status'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order (respecting foreign keys)
    op.drop_table('generation_jobs')
    op.drop_table('tasks')
    op.drop_table('audit_logs')
    op.drop_table('reviews')
    op.drop_table('assets')
    op.drop_table('storyboards')
    op.drop_table('chapters')
    op.drop_table('script_versions')
    op.drop_table('scripts')
    op.drop_table('model_providers')
    op.drop_table('project_members')
    op.drop_table('projects')
    op.drop_table('users')
