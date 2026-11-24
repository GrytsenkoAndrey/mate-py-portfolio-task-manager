from django.urls import path
from .views import (
    index,
    worker_form,
    worker_detail,
    TagListView,
    WorkerListView,
    TeamListView,
    TeamCreateView,
    TeamUpdateView,
    TeamDeleteView,
    ProjectListView,
    ProjectDetailView,
)

urlpatterns = [
    path("", index, name="index"),
    path("workers/", WorkerListView.as_view(), name="workers"),
    path("worker-form/", worker_form, name="worker-form"),
    path("worker-detail/<int:pk>/", worker_detail, name="worker-detail"),
    path("tags/", TagListView.as_view(), name="tags"),
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
]

app_name = "manager"
