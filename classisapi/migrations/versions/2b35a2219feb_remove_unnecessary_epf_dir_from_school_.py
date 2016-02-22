"""remove unnecessary epf dir from school table

Revision ID: 2b35a2219feb
Revises: 4917325bdc9a
Create Date: 2016-02-22 14:26:33.620610

"""

# revision identifiers, used by Alembic.
revision = '2b35a2219feb'
down_revision = '4917325bdc9a'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.drop_column('school', 'eportfolio_path')


def downgrade():
    op.add_column('school', sa.Column('eportfolio_path', sa.String(length=300), nullable=True))
