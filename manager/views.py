from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Prefetch, Q
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import generic

from .enums import PriorityEnum
from .forms import WorkerUpdateForm, TagForm, TeamForm, ProjectForm, TaskForm
from .models import Tag, Worker, Team, Project, Task


# Create your views here.
@login_required
def index(request):
    """View function for home page of site."""
    today = timezone.localdate()
    open_tasks = Task.objects.filter(is_completed=False)

    priority_counts = dict(
        open_tasks.values_list("priority").annotate(total=Count("id"))
    )
    priorities = [
        (priority.value, priority_counts.get(priority.value, 0))
        for priority in reversed(PriorityEnum)
    ]

    projects = Project.objects.annotate(
        tasks_total=Count("tasks", distinct=True),
        tasks_done=Count(
            "tasks",
            filter=Q(tasks__is_completed=True),
            distinct=True,
        ),
    ).order_by("name")
    for project in projects:
        project.progress = (
            round(project.tasks_done * 100 / project.tasks_total)
            if project.tasks_total
            else 0
        )

    my_tasks = (
        Task.objects.filter(project__team__members=request.user)
        .select_related("task_type", "project")
        .prefetch_related("tags")
        .distinct()
        .order_by("is_completed", "deadline", "name")
    )

    context = {
        "today": today,
        "open_tasks_count": open_tasks.count(),
        "done_tasks_count": Task.objects.filter(is_completed=True).count(),
        "overdue_tasks_count": open_tasks.filter(deadline__lt=today).count(),
        "workers_count": Worker.objects.count(),
        "teams_count": Team.objects.count(),
        "upcoming_tasks": open_tasks.select_related(
            "task_type", "project"
        ).order_by("deadline", "name")[:6],
        "projects": projects,
        "priorities": priorities,
        "my_tasks": my_tasks,
    }
    return render(request, "manager/index.html", context)


@login_required
def worker_form(request):
    """View function for worker form page."""
    if request.method == "POST":
        form = WorkerUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            worker = form.save()
            update_session_auth_hash(request, worker)
            return redirect("manager:worker-detail", pk=worker.pk)
    else:
        form = WorkerUpdateForm(instance=request.user)

    return render(request, "manager/worker-form.html", {"form": form})


@login_required
def worker_detail(request, pk):
    """View function for worker detail page."""
    worker = get_object_or_404(Worker, pk=pk)

    return render(request, "manager/worker-detail.html", {"worker": worker})


class WorkerListView(LoginRequiredMixin, generic.ListView):
    model = Worker
    template_name = "manager/workers.html"
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["workers_count"] = Worker.objects.count()
        return context


class TagListView(LoginRequiredMixin, generic.ListView):
    model = Tag
    queryset = Tag.objects.annotate(tasks_count=Count("tasks"))
    form_class = TagForm
    template_name = "manager/tags.html"
    paginate_by = 10
    ordering = ["name"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.setdefault("tag_form", self.form_class())
        return context

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
            return redirect("manager:tags")
        self.object_list = self.get_queryset()
        return self.render_to_response(self.get_context_data(tag_form=form))


class TagUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Tag
    form_class = TagForm
    template_name = "manager/tag-form.html"
    success_url = reverse_lazy("manager:tags")


class TagDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Tag
    template_name = "manager/tag-confirm-delete.html"
    success_url = reverse_lazy("manager:tags")


class TeamListView(LoginRequiredMixin, generic.ListView):
    model = Team
    queryset = Team.objects.prefetch_related(
        Prefetch(
            "members", queryset=Worker.objects.select_related("position")
        ),
        "projects"
    )
    template_name = "manager/teams.html"
    paginate_by = 10
    ordering = ["name"]


class TeamCreateView(LoginRequiredMixin, generic.CreateView):
    model = Team
    form_class = TeamForm
    template_name = "manager/team-form.html"
    success_url = reverse_lazy("manager:teams")


class TeamUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Team
    form_class = TeamForm
    template_name = "manager/team-form.html"
    success_url = reverse_lazy("manager:teams")


class TeamDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Team
    template_name = "manager/team-confirm-delete.html"
    success_url = reverse_lazy("manager:teams")


class ProjectListView(LoginRequiredMixin, generic.ListView):
    model = Project
    queryset = (
        Project.objects.select_related("team")
        .prefetch_related("team__members")
        .annotate(
            tasks_total=Count("tasks", distinct=True),
            tasks_done=Count(
                "tasks",
                filter=Q(tasks__is_completed=True),
                distinct=True,
            ),
        )
        .order_by("name")
    )
    template_name = "manager/projects.html"
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["teams"] = Team.objects.order_by("name")
        return context


class ProjectDetailView(LoginRequiredMixin, generic.DetailView):
    model = Project
    queryset = (
        Project.objects.select_related("team")
        .prefetch_related("team__members__position")
        .annotate(
            tasks_total=Count("tasks", distinct=True),
            tasks_done=Count(
                "tasks",
                filter=Q(tasks__is_completed=True),
                distinct=True,
            ),
        )
        .order_by("name")
    )
    template_name = "manager/project-detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tasks"] = (
            self.object.tasks.select_related("task_type")
            .prefetch_related("tags")
            .order_by("deadline", "name")
        )
        context["tasks_open"] = (
            self.object.tasks_total - self.object.tasks_done
        )
        context["progress"] = (
            round(self.object.tasks_done * 100 / self.object.tasks_total)
            if self.object.tasks_total
            else 0
        )
        context["days_left"] = (
            self.object.deadline - timezone.localdate()
        ).days
        return context


class ProjectCreateView(LoginRequiredMixin, generic.CreateView):
    model = Project
    form_class = ProjectForm
    template_name = "manager/project-form.html"
    success_url = reverse_lazy("manager:projects")


class ProjectUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = "manager/project-form.html"
    success_url = reverse_lazy("manager:projects")


class ProjectDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Project
    template_name = "manager/project-confirm-delete.html"
    success_url = reverse_lazy("manager:projects")


class TaskListView(LoginRequiredMixin, generic.ListView):
    model = Task
    queryset = (
        Task.objects.select_related("task_type", "project")
        .prefetch_related("tags")
        .order_by("deadline", "name")
    )
    template_name = "manager/tasks.html"
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tasks_count"] = Task.objects.count()
        context["projects_count"] = Project.objects.count()
        return context


class TaskDetailView(LoginRequiredMixin, generic.DetailView):
    model = Task
    queryset = (
        Task.objects.select_related("task_type", "project__team")
        .prefetch_related("tags", "project__team__members__position")
    )
    template_name = "manager/task-detail.html"


class TaskCreateView(LoginRequiredMixin, generic.CreateView):
    model = Task
    form_class = TaskForm
    template_name = "manager/task-form.html"
    success_url = reverse_lazy("manager:tasks")


class TaskUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Task
    form_class = TaskForm
    template_name = "manager/task-form.html"
    success_url = reverse_lazy("manager:tasks")


class TaskDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Task
    template_name = "manager/task-confirm-delete.html"
    success_url = reverse_lazy("manager:tasks")
