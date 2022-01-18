"""
Таблицы заполненыследующими данными:
homework:
id | text | deadline | teacher_id | created
1, 'do your job', 2023-01-03, 1, (2022, 1, 8, 18, 30, 26)
2, 'write an essay', 2023-01-01, 1, (2022, 1, 9, 10, 30, 26)
3, 'Jump', 2023-02-01, 2, (2022, 1, 10, 13, 30, 26)

student:
id | first_name | last_name
1, Ivan, Petrov
2, Andrey, Zvento

teacher:
id | first_name | last_name
1, Sergei, Tokarev
2, Alexey, Fedorov

homeworkresult:
id | author_id | homework_id | solution | created
1, 1, 1, 'I do my best', (2022, 1, 8, 18, 30, 26)
2, 2, 1, 'Done', (2022, 1, 10, 15, 30, 11)
3, 1, 2, 'essay', (2022, 1, 12, 10, 10, 11)
4, 2, 3, 'essay', (2022, 1, 15, 8, 30, 20)
"""
import csv

from oop_3 import Homework, HomeworkResult, Student, Teacher
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///main.db')
Base = declarative_base()

Session = sessionmaker(bind=engine)
Base.metadata.create_all(engine)
session = Session()

headers = ['text', 'student', 'created', 'teacher']
homeworks = []


with session:
    hwresults = session.query(HomeworkResult).all()
    for res in hwresults:
        hw = session.query(Homework).filter(Homework.id == res.homework_id).one()
        text = hw.text
        created = hw.created

        student = session.query(Student.first_name, Student.last_name).filter(Student.id == res.author_id).one()
        student_name = ' '.join(student)
        teacher = session.query(Teacher.first_name, Teacher.last_name).filter(Teacher.id == hw.teacher_id).one()
        teacher_name = ' '.join(teacher)

        homeworks.append([text, student_name, created, teacher_name])

with open('homeworks.csv', 'w') as f:
    writer = csv.writer(f)
    writer.writerow(headers)
    writer.writerows(homeworks)
