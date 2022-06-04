"""empty message

Revision ID: fdc720c8a58a
Revises: e24e9dbe0775
Create Date: 2022-06-02 19:21:10.747885

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'fdc720c8a58a'
down_revision = 'e24e9dbe0775'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('venue', sa.Column('created_at', sa.DateTime(), nullable=True))
    op.drop_column('venue', 'created_on')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('venue', sa.Column('created_on', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    op.drop_column('venue', 'created_at')
    # ### end Alembic commands ###