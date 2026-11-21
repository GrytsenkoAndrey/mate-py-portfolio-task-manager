from django.contrib.auth.decorators import login_required
from django.shortcuts import render

# Create your views here.


@login_required
def index(request):
    """View function for home page of site."""

    return render(request, "manager/index.html")


@login_required
def worker_form(request):
    """View function for worker form page."""

    return render(request, "manager/worker-form.html")


@login_required
def worker_detail(request):
    """View function for worker detail page."""

    return render(request, "manager/worker-detail.html")
