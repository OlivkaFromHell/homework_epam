"""insert data

Revision ID: 7d72ff61244c
Revises: 9c35d6f186bb
Create Date: 2022-01-09 00:54:05.797510

"""
import datetime

from alembic import op

# revision identifiers, used by Alembic.
revision = '7d72ff61244c'
down_revision = '9c35d6f186bb'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('INSERT INTO homework '
               f'VALUES (1, "do your job", "{datetime.date(2022, 1, 21)}",'
               f'"{datetime.datetime(2022, 1, 8, 18, 30, 26)}")')
    op.execute('INSERT INTO student '
               'VALUES (1, "Ivan", "Petrov")')
    op.execute('INSERT INTO teacher '
               'VALUES (1, "Sergei", "Tokarev")')
    op.execute('INSERT INTO homeworkresult '
               f'VALUES (1, 1, 1, "I do my best", "{datetime.datetime(2022, 1, 8, 18, 30, 26)}")')


def downgrade():
    pass
