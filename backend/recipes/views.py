from django.shortcuts import render
from django.http import HttpResponse


def index(request):
    return render(request, 'recipes/index.html')


def subscript(request):
    return HttpResponse("<h4>Мои подписки</h4>")
 