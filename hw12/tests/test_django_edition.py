import sqlite3
from pathlib import Path

db_path = Path(__file__).resolve().parent.parent.joinpath('django_edition/school/school.sqlite3')
print('\n', db_path)

con = sqlite3.connect(db_path)
cur = con.cursor()


def test_homework():
    cur.execute('SELECT * FROM base_homework where id=1')
    data = cur.fetchone()
    assert data[1] == 'write an essay'


def test_student():
    cur.execute('SELECT * FROM base_student where id=1')
    data = cur.fetchone()
    assert data[1] == 'Andrey'


def test_teacher():
    cur.execute('SELECT * FROM base_teacher where id=1')
    data = cur.fetchone()
    assert data[1] == 'Alex'


def test_hwresult():
    cur.execute('SELECT * FROM base_homeworkresult where id=1')
    data = cur.fetchone()
    assert data[1] == 'essay'
    con.close()
