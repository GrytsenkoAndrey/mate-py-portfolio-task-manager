from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from .forms import WorkerUpdateForm


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
            return redirect("manager:worker-detail")
    else:
        form = WorkerUpdateForm(instance=request.user)

    return render(request, "manager/worker-form.html", {"form": form})


@login_required
def worker_detail(request):
    """View function for worker detail page."""

    return render(request, "manager/worker-detail.html")
