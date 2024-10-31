from django.shortcuts import render
from django.http import HttpResponse


def analyser(request):
    return HttpResponse('Analyser Page!')
