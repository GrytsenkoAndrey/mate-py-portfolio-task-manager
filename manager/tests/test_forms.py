from django.test import TestCase

from manager.enums import PriorityEnum
from manager.forms import TagForm, TaskForm, WorkerUpdateForm
from manager.models import (
    Position,
    Project,
    Tag,
    TaskType,
    Team,
    Worker,
)


class WorkerUpdateFormTests(TestCase):
    def setUp(self):
        self.position = Position.objects.create(name="Developer")
        self.worker = Worker.objects.create_user(
            username="jane",
            password="old-password",
            first_name="Jane",
            last_name="Doe",
            email="jane@example.com",
            position=self.position,
        )

    def get_form_data(self, **overrides):
        data = {
            "first_name": self.worker.first_name,
            "last_name": self.worker.last_name,
            "username": self.worker.username,
            "email": self.worker.email,
            "position": self.position.pk,
            "password1": "",
            "password2": "",
        }
        data.update(overrides)
        return data

    def test_password_mismatch_is_invalid(self):
        form = WorkerUpdateForm(
            data=self.get_form_data(
                password1="NewPassword1",
                password2="DifferentPassword1",
            ),
            instance=self.worker,
        )

        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)

    def test_matching_password_is_saved(self):
        form = WorkerUpdateForm(
            data=self.get_form_data(
                password1="NewPassword1",
                password2="NewPassword1",
            ),
            instance=self.worker,
        )

        self.assertTrue(form.is_valid(), form.errors)
        worker = form.save()

        self.assertTrue(worker.check_password("NewPassword1"))


class TaskFormTests(TestCase):
    def setUp(self):
        position = Position.objects.create(name="Developer")
        worker = Worker.objects.create_user(
            username="jane",
            password="password",
            position=position,
        )
        team = Team.objects.create(name="Platform")
        team.members.add(worker)
        self.project = Project.objects.create(
            name="Website",
            deadline="2027-01-15",
            team=team,
        )
        self.task_type = TaskType.objects.create(name="Feature")
        self.tag = Tag.objects.create(name="backend")

    def get_form_data(self, **overrides):
        data = {
            "name": "Add login",
            "description": "Implement login flow",
            "priority": PriorityEnum.HIGH.value,
            "task_type": self.task_type.pk,
            "deadline": "2027-01-15",
            "project": self.project.pk,
            "tags": [self.tag.pk],
            "is_completed": "",
        }
        data.update(overrides)
        return data

    def test_valid_task_data_is_accepted(self):
        form = TaskForm(data=self.get_form_data())

        self.assertTrue(form.is_valid(), form.errors)

    def test_invalid_priority_is_rejected(self):
        form = TaskForm(data=self.get_form_data(priority="Critical"))

        self.assertFalse(form.is_valid())
        self.assertIn("priority", form.errors)


class TagFormTests(TestCase):
    def test_valid_tag_data_is_accepted(self):
        form = TagForm(data={"name": "backend"})

        self.assertTrue(form.is_valid(), form.errors)
        tag = form.save()

        self.assertEqual(
            Tag.objects.get(pk=tag.pk).name,
            "backend",
        )
