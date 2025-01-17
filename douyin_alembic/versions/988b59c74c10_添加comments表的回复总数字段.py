"""添加comments表的回复总数字段

Revision ID: 988b59c74c10
Revises: 165b97a49842
Create Date: 2020-02-24 17:08:00.563939

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '988b59c74c10'
down_revision = '165b97a49842'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('comments', sa.Column('reply_comment_total', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('comments', 'reply_comment_total')
    # ### end Alembic commands ###
