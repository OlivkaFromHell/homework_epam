"""create table

Revision ID: 54d3619b4c8a
Revises:
Create Date: 2022-01-17 22:16:44.964078

"""
import datetime

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '54d3619b4c8a'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'homework',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('text', sa.String),
        sa.Column('deadline', sa.Date),
        sa.Column('teacher_id', sa.Date),
        sa.Column('created', sa.DateTime, default=datetime.datetime.now()),
    )
    op.create_table(
        'student',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('first_name', sa.String),
        sa.Column('last_name', sa.String),
    )
    op.create_table(
        'teacher',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('first_name', sa.String),
        sa.Column('last_name', sa.String),
    )
    op.create_table(
        'homeworkresult',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('author_id', sa.Integer, sa.ForeignKey('author.id')),
        sa.Column('homework_id', sa.Integer, sa.ForeignKey('homework.id')),
        sa.Column('solution', sa.String),
        sa.Column('created', sa.DateTime, default=datetime.datetime.now()),
    )


def downgrade():
    pass
