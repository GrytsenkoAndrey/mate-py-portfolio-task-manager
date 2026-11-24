from django.contrib.auth.models import AbstractUser
from django.db import models
from .enums import PositionTypeEnum, TaskTypeEnum, PriorityEnum


# Create your models here.
class Position(models.Model):
    name = models.CharField(
        max_length=255,
        default=PositionTypeEnum.DEVELOPER.value,
    )

    def __str__(self):
        return self.name


class Worker(AbstractUser):
    position = models.ForeignKey(Position, on_delete=models.CASCADE)

    def get_initials(self):
        return f"{self.first_name[0]}{self.last_name[0]}"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return self.get_full_name()


class Team(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(default="")
    members = models.ManyToManyField(Worker, related_name="teams")


class Tag(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class TaskType(models.Model):
    name = models.CharField(max_length=255, default=TaskTypeEnum.FEATURE.value)

    def __str__(self):
        return self.name


class Project(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(default="")
    deadline = models.DateField()
    team = models.ForeignKey(
        Team, on_delete=models.CASCADE, related_name="projects"
    )

    def __str__(self):
        return self.name


class Task(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    deadline = models.DateField()
    is_completed = models.BooleanField(default=False)
    priority = models.CharField(
        max_length=63,
        default=PriorityEnum.NORMAL.value,
    )
    task_type = models.ForeignKey(
        TaskType, on_delete=models.CASCADE, related_name="tasks"
    )
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="tasks"
    )
    tags = models.ManyToManyField(Tag, related_name="tasks")
