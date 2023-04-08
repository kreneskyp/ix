from django.http import HttpResponse
from django.shortcuts import render


def status(request):
    return HttpResponse("1")


def index(request):
    return render(request, "index.html")
