"""add eportfolio path column to school

Revision ID: 413c3428b33b
Revises: 
Create Date: 2016-02-03 09:43:42.681328

"""

# revision identifiers, used by Alembic.
revision = '413c3428b33b'
down_revision = None
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('school', sa.Column('eportfolio_path', sa.String(300)))


def downgrade():
    op.drop_column('school', 'eportfolio_path')
