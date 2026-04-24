from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render


def inicio(request: HttpRequest) -> HttpResponse:
    return redirect("catalogo")


def teste(request: HttpRequest) -> HttpResponse:
    return render(request, "teste.html")
