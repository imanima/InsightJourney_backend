"""update action items schema

Revision ID: update_action_items_schema
Revises: previous_revision
Create Date: 2024-03-21

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'update_action_items_schema'
down_revision = 'previous_revision'
branch_labels = None
depends_on = None

def upgrade():
    # Rename content to title
    op.alter_column('action_items', 'content', new_column_name='title')
    
    # Add new columns
    op.add_column('action_items', sa.Column('description', sa.Text(), nullable=True))
    op.add_column('action_items', sa.Column('priority', sa.String(50), nullable=False, server_default='medium'))
    op.add_column('action_items', sa.Column('topic', sa.String(255), nullable=True))
    
    # Update status enum
    op.execute("""
        ALTER TABLE action_items 
        DROP CONSTRAINT IF EXISTS action_items_status_check,
        ADD CONSTRAINT action_items_status_check 
        CHECK (status IN ('completed', 'in_progress', 'not_started'))
    """)
    
    # Update existing records
    op.execute("""
        UPDATE action_items 
        SET status = CASE 
            WHEN status = 'pending' THEN 'not_started'
            ELSE status
        END
    """)

def downgrade():
    # Revert status enum
    op.execute("""
        ALTER TABLE action_items 
        DROP CONSTRAINT IF EXISTS action_items_status_check,
        ADD CONSTRAINT action_items_status_check 
        CHECK (status IN ('pending', 'completed'))
    """)
    
    # Update existing records
    op.execute("""
        UPDATE action_items 
        SET status = CASE 
            WHEN status = 'not_started' THEN 'pending'
            ELSE status
        END
    """)
    
    # Remove new columns
    op.drop_column('action_items', 'topic')
    op.drop_column('action_items', 'priority')
    op.drop_column('action_items', 'description')
    
    # Rename title back to content
    op.alter_column('action_items', 'title', new_column_name='content') 