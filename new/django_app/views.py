"""
views - контроллеры(вью) - т.е. бизнес логика
"""
import sqlite3
from django.shortcuts import render, redirect
from django_app import utils
from django.contrib.auth import authenticate, login as l, logout as lo


def home(request):
    return render(request, "home.html", context={})


def about(request):
    return render(request, "about.html", context={})


def profile(request, username):
    return render(request, "profile.html", context={"username": username})


def test(request):
    return render(request, "test.html")


def product_list(request):
    return render(request, "product_list.html", context={})


def login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            l(request, user)
            return redirect("profile", username=username)

    return render(request, "login.html", context={})


def register(request):
    return render(request, "register.html", context={})

def logout(request):
    lo(request)
    return redirect("home")