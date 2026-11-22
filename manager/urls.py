from django.urls import path
from .views import (
    index,
    worker_form,
    worker_detail,
    TagListView,
)

urlpatterns = [
    path("", index, name="index"),
    path("worker-form/", worker_form, name="worker-form"),
    path("worker-detail/", worker_detail, name="worker-detail"),
    path("tags/", TagListView.as_view(), name="tags"),
]

app_name = "manager"
