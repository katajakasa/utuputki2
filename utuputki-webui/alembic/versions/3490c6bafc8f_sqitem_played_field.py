"""sqitem played field

Revision ID: 3490c6bafc8f
Revises: 10f1d9760a41
Create Date: 2015-10-18 21:43:49.918000

"""

# revision identifiers, used by Alembic.
revision = '3490c6bafc8f'
down_revision = '10f1d9760a41'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('sourcequeueitem', sa.Column('played', sa.Boolean(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('sourcequeueitem', 'played')
    ### end Alembic commands ###
