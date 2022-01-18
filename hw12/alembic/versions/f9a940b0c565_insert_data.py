"""insert data

Revision ID: f9a940b0c565
Revises: 54d3619b4c8a
Create Date: 2022-01-17 22:19:59.775685

"""
import datetime

from alembic import op

# revision identifiers, used by Alembic.
revision = 'f9a940b0c565'
down_revision = '54d3619b4c8a'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('INSERT INTO homework '
               f'VALUES (1, "do your job", "{datetime.date(2023, 1, 3)}", 1, '
               f'"{datetime.datetime(2022, 1, 8, 18, 30, 26)}")')
    op.execute('INSERT INTO homework '
               f'VALUES (2, "write an essay", "{datetime.date(2023, 1, 1)}", 1,'
               f'"{datetime.datetime(2022, 1, 9, 10, 30, 26)}")')
    op.execute('INSERT INTO homework '
               f'VALUES (3, "Jump", "{datetime.date(2022, 2, 1)}", 2,'
               f'"{datetime.datetime(2022, 1, 10, 13, 30, 26)}")')

    op.execute('INSERT INTO student '
               'VALUES (1, "Ivan", "Petrov")')
    op.execute('INSERT INTO student '
               'VALUES (2, "Andrey", "Zvento")')

    op.execute('INSERT INTO teacher '
               'VALUES (1, "Sergei", "Tokarev")')
    op.execute('INSERT INTO teacher '
               'VALUES (2, "Alexey", "Fedorov")')

    op.execute('INSERT INTO homeworkresult '
               f'VALUES (1, 1, 1, "I do my best", "{datetime.datetime(2022, 1, 8, 18, 30, 26)}")')
    op.execute('INSERT INTO homeworkresult '
               f'VALUES (2, 2, 1, "Done", "{datetime.datetime(2022, 1, 10, 15, 30, 11)}")')
    op.execute('INSERT INTO homeworkresult '
               f'VALUES (3, 1, 2, "essay", "{datetime.datetime(2022, 1, 12, 10, 10, 11)}")')
    op.execute('INSERT INTO homeworkresult '
               f'VALUES (4, 2, 3, "essay", "{datetime.datetime(2022, 1, 15, 8, 30, 20)}")')


def downgrade():
    pass
