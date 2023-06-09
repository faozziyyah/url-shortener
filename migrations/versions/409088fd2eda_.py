"""empty message

Revision ID: 409088fd2eda
Revises: 9749df0d85da
Create Date: 2023-06-24 12:57:45.917042

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '409088fd2eda'
down_revision = '9749df0d85da'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=100), nullable=True),
    sa.Column('email', sa.String(), nullable=True),
    sa.Column('confirmed', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('short_urls', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(None, 'user', ['user_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('short_urls', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('user_id')

    op.drop_table('user')
    # ### end Alembic commands ###
