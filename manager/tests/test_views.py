from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from manager.enums import PriorityEnum, TaskTypeEnum, PositionTypeEnum
from manager.models import (
    Position,
    Project,
    Tag,
    Task,
    TaskType,
    Team,
    Worker,
)


class ManagerViewTests(TestCase):
    def setUp(self):
        self.position = Position.objects.create(
            name=PositionTypeEnum.DEVELOPER.value
        )
        self.worker = Worker.objects.create_user(
            username="jane",
            password="old-password",
            first_name="Jane",
            last_name="Doe",
            email="jane@example.com",
            position=self.position,
        )
        self.team = Team.objects.create(name="Platform")
        self.team.members.add(self.worker)
        self.project = Project.objects.create(
            name="Website",
            deadline="2027-01-15",
            team=self.team,
        )
        self.task_type = TaskType.objects.create(
            name=TaskTypeEnum.FEATURE.value
        )
        self.tag = Tag.objects.create(name="backend")

    def login(self):
        self.client.force_login(self.worker)

    def create_task(self, name, is_completed=False, deadline=None):
        return Task.objects.create(
            name=name,
            description="Task description",
            deadline=deadline or timezone.localdate(),
            is_completed=is_completed,
            priority=PriorityEnum.NORMAL.value,
            task_type=self.task_type,
            project=self.project,
        )

    def test_login_is_required_for_main_views(self):
        for view_name, args in (
            ("manager:index", ()),
            ("manager:tags", ()),
            ("manager:teams", ()),
            ("manager:projects", ()),
            ("manager:tasks", ()),
            ("manager:task-detail", (1,)),
        ):
            with self.subTest(view=view_name):
                response = self.client.get(reverse(view_name, args=args))

                self.assertEqual(response.status_code, 302)
                self.assertIn("/accounts/login/", response.url)

    def test_index_displays_counts_and_project_progress(self):
        today = timezone.localdate()
        self.create_task(
            "Overdue", deadline=today - timedelta(days=1)
        )
        self.create_task("Open", deadline=today + timedelta(days=1))
        self.create_task("Done", is_completed=True)
        self.login()

        response = self.client.get(reverse("manager:index"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["open_tasks_count"], 2)
        self.assertEqual(response.context["done_tasks_count"], 1)
        self.assertEqual(response.context["overdue_tasks_count"], 1)
        self.assertEqual(response.context["workers_count"], 1)
        self.assertEqual(response.context["teams_count"], 1)
        project = response.context["projects"][0]
        self.assertEqual(project.progress, 33)

    def test_tag_list_creates_a_tag(self):
        self.login()

        response = self.client.post(
            reverse("manager:tags"), {"name": "backend"}
        )

        self.assertRedirects(response, reverse("manager:tags"))
        self.assertTrue(Tag.objects.filter(name="backend").exists())

    def test_tag_list_renders_invalid_submission(self):
        self.login()

        response = self.client.post(
            reverse("manager:tags"), {"name": ""}
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("name", response.context["tag_form"].errors)

    def test_team_project_and_task_can_be_created(self):
        self.login()

        team_response = self.client.post(
            reverse("manager:team-create"),
            {
                "name": "Design",
                "description": "Design team",
                "members": [self.worker.pk],
            },
        )
        new_team = Team.objects.get(name="Design")
        self.assertRedirects(team_response, reverse("manager:teams"))

        project_response = self.client.post(
            reverse("manager:project-create"),
            {
                "name": "Mobile app",
                "description": "Mobile application",
                "team": new_team.pk,
                "deadline": "2027-01-15",
            },
        )
        new_project = Project.objects.get(name="Mobile app")
        self.assertRedirects(project_response, reverse("manager:projects"))

        task_response = self.client.post(
            reverse("manager:task-create"),
            {
                "name": "Add navigation",
                "description": "Create app navigation",
                "priority": PriorityEnum.HIGH.value,
                "task_type": self.task_type.pk,
                "deadline": "2027-01-15",
                "project": new_project.pk,
                "tags": [self.tag.pk],
                "is_completed": "",
            },
        )

        self.assertRedirects(task_response, reverse("manager:tasks"))
        self.assertTrue(
            new_project.tasks.filter(name="Add navigation").exists()
        )

    def test_project_detail_shows_task_progress(self):
        self.create_task("Open")
        self.create_task("Done", is_completed=True)
        self.login()

        response = self.client.get(
            reverse("manager:project-detail", args=[self.project.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["progress"], 50)
        self.assertEqual(response.context["tasks_open"], 1)

    def test_task_detail_displays_task_data(self):
        task = self.create_task("Add sign-in")
        task.tags.add(self.tag)
        self.login()

        response = self.client.get(
            reverse("manager:task-detail", args=[task.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["task"], task)
        self.assertContains(response, "Add sign-in")
        self.assertContains(response, "Task description")
        self.assertContains(response, "#backend")
        self.assertContains(response, self.project.name)
        self.assertContains(response, self.worker.get_full_name())

    def test_password_change_keeps_worker_logged_in(self):
        self.login()

        response = self.client.post(
            reverse("manager:worker-form"),
            {
                "first_name": "Jane",
                "last_name": "Doe",
                "username": "jane",
                "email": "jane@example.com",
                "position": self.position.pk,
                "password1": "NewPassword1",
                "password2": "NewPassword1",
            },
        )

        self.assertRedirects(
            response,
            reverse("manager:worker-detail", args=[self.worker.pk]),
        )
        self.assertEqual(
            self.client.get(reverse("manager:index")).status_code,
            200,
        )
