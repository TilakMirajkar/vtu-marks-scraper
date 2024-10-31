from django.shortcuts import render
from django.http import HttpResponse


def home(request):
    return render(request, 'home.html')

def tutorial(request):
    return render(request, 'tutorial.html')

def project(request):
    return render(request, 'project.html')
