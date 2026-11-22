from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.views import generic

from .forms import WorkerUpdateForm, TagForm
from .models import Tag, Worker


# Create your views here.
@login_required
def index(request):
    """View function for home page of site."""

    return render(request, "manager/index.html")


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
    form_class = TagForm
    template_name = "manager/tags.html"
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tag_form"] = self.form_class()
        return context

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
            return redirect("manager:tags")
        self.object_list = self.get_queryset()
        context = self.get_context_data()
        context["tag_form"] = form
        return self.render_to_response(context)
