from django.http import HttpResponse
from django.shortcuts import render, redirect
from langsmith import Client as LangsmithClient


def status(request):
    return HttpResponse("1")


def index(request):
    return render(request, "index.html")


def langsmith(request, run_id):
    """Redirect to the Langsmith run details for the given run_id."""
    client = LangsmithClient()
    run = client.read_run(run_id)
    return redirect(run.url)
