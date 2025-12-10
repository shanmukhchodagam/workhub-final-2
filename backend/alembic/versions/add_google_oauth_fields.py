"""Add Google OAuth fields to users table

Revision ID: add_google_oauth_fields
Revises: 
Create Date: 2025-12-08 11:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'add_google_oauth_fields'
down_revision = None
depends_on = None

def upgrade():
    """Add Google OAuth fields to users table"""
    # Add Google OAuth columns
    op.add_column('users', sa.Column('google_id', sa.String(), nullable=True))
    op.add_column('users', sa.Column('profile_picture', sa.String(), nullable=True))
    op.add_column('users', sa.Column('auth_provider', sa.String(), nullable=False, server_default='local'))
    
    # Make hashed_password nullable for Google OAuth users
    op.alter_column('users', 'hashed_password', nullable=True)
    
    # Add indexes
    op.create_index('ix_users_google_id', 'users', ['google_id'], unique=True)

def downgrade():
    """Remove Google OAuth fields from users table"""
    op.drop_index('ix_users_google_id', table_name='users')
    op.drop_column('users', 'auth_provider')
    op.drop_column('users', 'profile_picture')
    op.drop_column('users', 'google_id')
    op.alter_column('users', 'hashed_password', nullable=False)