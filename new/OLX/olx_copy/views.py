from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.core.cache import cache
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from .utils import decorator_error_handler


def about(request):
    return render(request, "about.html", context={})


# @decorator_error_handler
def home(request):
    return render(request, "home.html", context={})


@decorator_error_handler
def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            return render(request, "register.html", {"error": "Passwords do not match"})

        existing_user = User.objects.filter(username=username).exists()
        if existing_user:
            return render(
                request, "register.html", {"error": "Username already exists"}
            )

        user = User.objects.create_user(
            username=username,
            password=password,
        )

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("profile", username=username)
        else:
            return render(
                request,
                "register.html",
                {"error": "Failed to log in. Please try again."},
            )

    return render(request, "register.html", context={})


def logout_view(request):
    logout(request)
    return redirect("home")


@decorator_error_handler
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("home")

    return render(request, "login.html", context={})


@decorator_error_handler
def profile(request, username):
    return render(request, "profile.html", context={"username": username})
