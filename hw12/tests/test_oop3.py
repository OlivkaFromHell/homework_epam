import datetime

from hw12.oop_3 import Homework, HomeworkResult, Student, Teacher


def test_homework():
    text = 'write an essay'
    deadline = datetime.date(2022, 2, 1)
    hw = Homework(text=text, deadline=deadline)
    assert hw.text == text
    assert hw.deadline == deadline


def test_student():
    first_name = 'Andrey'
    last_name = 'Zetkov'
    st = Student(id=1, first_name=first_name, last_name=last_name)
    assert st.first_name == first_name
    assert st.last_name == last_name


def test_teacher():
    first_name = 'Andrey'
    last_name = 'Zetkov'
    t = Teacher(id=1, first_name=first_name, last_name=last_name)
    assert t.first_name == first_name
    assert t.last_name == last_name


def test_homeworkresult():
    hw = Homework(id=1, text='write an essay', deadline=datetime.date(2022, 2, 1), )
    st = Student(id=1, first_name='Andrey', last_name='Petrov')

    hwr = HomeworkResult(solution='essay', homework=hw, student=st)
    assert hwr.solution == 'essay'
    assert hwr.homework == hw
    assert hwr.homework.id == 1
    assert hwr.student.id == 1
