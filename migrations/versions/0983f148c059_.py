"""empty message

Revision ID: 0983f148c059
Revises: 1e6436d12edc
Create Date: 2022-06-03 15:25:21.382807

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0983f148c059'
down_revision = '1e6436d12edc'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('album',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('artist_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['artist_id'], ['artist.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('song',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('album_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['album_id'], ['album.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('song')
    op.drop_table('album')
    # ### end Alembic commands ###