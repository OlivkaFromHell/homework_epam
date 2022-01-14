"""
Using ORM framework of your choice,
create models classes created in Homework 6 (Teachers, Students, Homework and others).
- Target database should be sqlite (filename main.db localted in current directory)
- ORM framework should support migrations.

Utilizing that framework capabilities, create
 - a migration file, creating all necessary database structures.
 - a migration file (separate) creating at least one record in each created database table
 - (*) optional task: write standalone script (get_report.py) that retrieves
and stores the following information into CSV file report.csv
     for all done (completed) homeworks:
         Student name (who completed homework)
         Creation date
         Teacher name who created homework


Utilize ORM capabilities as much as possible, avoiding executing raw SQL queries.
"""
import datetime

from sqlalchemy import (Column, ColumnDefault, Date, DateTime, ForeignKey,
                        Integer, String, create_engine)
from sqlalchemy.ext.declarative import AbstractConcreteBase, declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

engine = create_engine('sqlite:///main.db')
Base = declarative_base()


class Homework(Base):
    __tablename__ = 'homework'

    id = Column(Integer, primary_key=True)
    text = Column(String)
    deadline = Column(Date)
    created = Column(DateTime(timezone=True), server_default=func.now())  # ColumnDefault()
    homeworkresult = relationship('HomeworkResult', back_populates='homework')

    def __repr__(self):
        return "<Homework(text='%s', deadline='%s', created='%s')>" % (
            self.text, self.deadline, self.created)


class User(AbstractConcreteBase, Base):
    first_name = Column(String)
    last_name = Column(String)


class Student(User):
    __tablename__ = 'student'

    id = Column(Integer, primary_key=True)
    homeworkresult = relationship('HomeworkResult', back_populates='student')


class Teacher(User):
    __tablename__ = 'teacher'

    id = Column(Integer, primary_key=True)


class HomeworkResult(Base):
    __tablename__ = 'homeworkresult'

    id = Column(Integer, primary_key=True)
    solution = Column(String)
    created = Column(DateTime, ColumnDefault(datetime.datetime.now()))
    homework_id = Column(Integer, ForeignKey('homework.id'))
    student_id = Column(Integer, ForeignKey('student.id'))
    homework = relationship('Homework', back_populates='homeworkresult')
    student = relationship('Student', back_populates='homeworkresult')
