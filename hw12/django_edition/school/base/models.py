from django.db import models


class Homework(models.Model):
    text = models.CharField(max_length=250)
    deadline = models.DateField()
    created = models.DateTimeField(auto_now_add=True, blank=True)


class User(models.Model):
    class Meta:
        abstract = True

    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)


class Student(User):
    pass


class Teacher(User):
    pass


class HomeworkResult(models.Model):
    author = models.ForeignKey('Student', on_delete=models.CASCADE)
    homework = models.ForeignKey('Homework', on_delete=models.CASCADE)
    solution = models.CharField(max_length=250)
    created = models.DateTimeField(auto_now_add=True, blank=True)
