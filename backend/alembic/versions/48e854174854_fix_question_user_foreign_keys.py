"""fix_question_user_foreign_keys

Revision ID: 48e854174854
Revises: 22320f141c6f
Create Date: 2025-06-05 22:52:28.098913

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '48e854174854'
down_revision: Union[str, None] = '22320f141c6f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Drop existing question tables if they exist (they might have been created by direct model creation)
    op.execute("DROP TABLE IF EXISTS question_set_questions CASCADE")
    op.execute("DROP TABLE IF EXISTS question_feedback CASCADE")
    op.execute("DROP TABLE IF EXISTS question_sets CASCADE")
    op.execute("DROP TABLE IF EXISTS questions CASCADE")
    
    # Create questions table with proper foreign key to users
    op.create_table('questions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('question_text', sa.Text(), nullable=False),
        sa.Column('question_type', sa.String(), nullable=False),
        sa.Column('correct_answer', sa.JSON(), nullable=True),
        sa.Column('options', sa.JSON(), nullable=True),
        sa.Column('explanation', sa.Text(), nullable=True),
        sa.Column('bloom_level', sa.String(), nullable=True),
        sa.Column('difficulty', sa.String(), nullable=True),
        sa.Column('topic', sa.String(), nullable=True),
        sa.Column('document_id', sa.Integer(), nullable=True),
        sa.Column('source_content', sa.JSON(), nullable=True),
        sa.Column('model_used', sa.String(), nullable=True),
        sa.Column('generation_time', sa.Float(), nullable=True),
        sa.Column('raw_llm_response', sa.Text(), nullable=True),
        sa.Column('upvotes', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('downvotes', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('difficulty_rating', sa.Float(), nullable=True),
        sa.Column('quality_score', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_questions_id'), 'questions', ['id'], unique=False)
    op.create_index(op.f('ix_questions_user_id'), 'questions', ['user_id'], unique=False)
    
    # Create question_feedback table with proper foreign key to users
    op.create_table('question_feedback',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('question_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('vote', sa.String(), nullable=True),
        sa.Column('difficulty_rating', sa.Integer(), nullable=True),
        sa.Column('quality_rating', sa.Integer(), nullable=True),
        sa.Column('comments', sa.Text(), nullable=True),
        sa.Column('is_helpful', sa.Boolean(), nullable=True),
        sa.Column('is_accurate', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['question_id'], ['questions.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_question_feedback_id'), 'question_feedback', ['id'], unique=False)
    
    # Create question_sets table with proper foreign key to users
    op.create_table('question_sets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.Column('source_documents', sa.JSON(), nullable=True),
        sa.Column('question_types', sa.JSON(), nullable=True),
        sa.Column('bloom_levels', sa.JSON(), nullable=True),
        sa.Column('difficulty_mix', sa.JSON(), nullable=True),
        sa.Column('total_questions', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('avg_difficulty', sa.Float(), nullable=True),
        sa.Column('completion_rate', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_question_sets_id'), 'question_sets', ['id'], unique=False)
    op.create_index(op.f('ix_question_sets_user_id'), 'question_sets', ['user_id'], unique=False)
    
    # Create association table for many-to-many relationship
    op.create_table('question_set_questions',
        sa.Column('question_set_id', sa.Integer(), nullable=False),
        sa.Column('question_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['question_id'], ['questions.id'], ),
        sa.ForeignKeyConstraint(['question_set_id'], ['question_sets.id'], ),
        sa.PrimaryKeyConstraint('question_set_id', 'question_id')
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('question_set_questions')
    op.drop_index(op.f('ix_question_sets_user_id'), table_name='question_sets')
    op.drop_index(op.f('ix_question_sets_id'), table_name='question_sets')
    op.drop_table('question_sets')
    op.drop_index(op.f('ix_question_feedback_id'), table_name='question_feedback')
    op.drop_table('question_feedback')
    op.drop_index(op.f('ix_questions_user_id'), table_name='questions')
    op.drop_index(op.f('ix_questions_id'), table_name='questions')
    op.drop_table('questions')
