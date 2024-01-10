from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.core.cache import cache
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from .utils import decorator_error_handler
from olx_copy import models


def about(request):
    return render(request, "about.html", context={})


def search(request):
    if request.method == "POST":
        _search = request.POST.get("search", "")
        _items = models.Item.objects.all().filter(
            is_active=True, title__icontains=_search
        )
        return render(request, "item.html", context={"items": _items})


@decorator_error_handler
def home(request):
    categories = models.CategoryItem.objects.all()
    return render(request, "home.html", context={"categories": categories})


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


@decorator_error_handler
def item(request, item_slug: str):
    cat = models.CategoryItem.objects.get(slug=item_slug)
    _item = models.Item.objects.all().filter(is_active=True, category=cat)
    return render(request, "item.html", context={"items": _item})

@decorator_error_handler
def items(request, slug_name: str):
    cat = models.Category.objects.get(slug=slug_name)
    _items = models.Item.objects.all().filter(is_active=True, category=cat)
    return render(request, "item.html", {"items": _items})

@decorator_error_handler
def category(request):
    categories = models.CategoryItem.objects.all()
    return render(request, "category.html", {"categories": categories})