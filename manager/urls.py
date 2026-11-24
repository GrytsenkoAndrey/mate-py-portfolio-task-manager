from django.urls import path
from .views import (
    index,
    worker_form,
    worker_detail,
    TagListView,
    TagUpdateView,
    TagDeleteView,
    WorkerListView,
    TeamListView,
    TeamCreateView,
    TeamUpdateView,
    TeamDeleteView,
    ProjectListView,
    ProjectDetailView,
    ProjectCreateView,
    ProjectUpdateView,
    ProjectDeleteView,
    TaskListView,
    TaskCreateView,
    TaskUpdateView,
    TaskDeleteView,
)

urlpatterns = [
    path("", index, name="index"),
    path("workers/", WorkerListView.as_view(), name="workers"),
    path("worker-form/", worker_form, name="worker-form"),
    path("worker-detail/<int:pk>/", worker_detail, name="worker-detail"),
    path("tags/", TagListView.as_view(), name="tags"),
    path(
        "tags/<int:pk>/update/",
        TagUpdateView.as_view(),
        name="tag-update",
    ),
    path(
        "tags/<int:pk>/delete/",
        TagDeleteView.as_view(),
        name="tag-delete",
    ),
    path("teams/", TeamListView.as_view(), name="teams"),
    path("teams/create/", TeamCreateView.as_view(), name="team-create"),
    path(
        "teams/<int:pk>/update/",
        TeamUpdateView.as_view(),
        name="team-update",
    ),
    path(
        "teams/<int:pk>/delete/",
        TeamDeleteView.as_view(),
        name="team-delete",
    ),
    path("projects/", ProjectListView.as_view(), name="projects"),
    path(
        "project-detail/<int:pk>/",
        ProjectDetailView.as_view(),
        name="project-detail",
    ),
    path(
        "projects/create/",
        ProjectCreateView.as_view(),
        name="project-create",
    ),
    path(
        "projects/<int:pk>/update/",
        ProjectUpdateView.as_view(),
        name="project-update",
    ),
    path(
        "projects/<int:pk>/delete/",
        ProjectDeleteView.as_view(),
        name="project-delete",
    ),
    path("tasks/", TaskListView.as_view(), name="tasks"),
    path("tasks/create/", TaskCreateView.as_view(), name="task-create"),
    path(
        "tasks/<int:pk>/update/",
        TaskUpdateView.as_view(),
        name="task-update",
    ),
    path(
        "tasks/<int:pk>/delete/",
        TaskDeleteView.as_view(),
        name="task-delete",
    ),
]

app_name = "manager"
