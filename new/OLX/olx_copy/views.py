import datetime
from django.http import Http404
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .utils import decorator_error_handler
from olx_copy import models
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def about(request):
    return render(request, "about.html", context={})


@decorator_error_handler
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
    vips = (
        models.Vip.objects.all()
        .filter(expired__gt=datetime.datetime.now())
        .order_by("priority", "-article")
    )
    return render(
        request, "home.html", context={"categories": categories, "vips": vips}
    )


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
def add_review(request, product_id):
    if request.method == "POST":
        product = get_object_or_404(models.Item, id=product_id)
        content = request.POST.get("content")
        models.Review.objects.create(
            product=product, user=request.user, content=content, is_visible=True
        )
    return redirect("product_detail", product_id=product_id)


@decorator_error_handler
def product_detail(request, product_id):
    try:
        product = models.Item.objects.get(id=product_id)
    except models.Item.DoesNotExist:
        raise Http404("Product not found")

    reviews = models.Review.objects.filter(product=product).order_by("-created_at")

    if not request.user.is_staff:
        reviews = reviews.filter(is_visible=True)

    paginator = Paginator(reviews, 3)
    page = request.GET.get("page", 1)
    try:
        paginated_reviews = paginator.page(page)
    except PageNotAnInteger:
        paginated_reviews = paginator.page(1)
    except EmptyPage:
        paginated_reviews = paginator.page(paginator.num_pages)

    image_url = product.get_image_url()

    if (
        request.method == "POST"
        and request.user.is_staff
        and request.user.is_authenticated
    ):
        review_id = request.POST.get("review_id")
        action = request.POST.get("action")

        try:
            review = models.Review.objects.get(id=review_id, product=product)
        except models.Review.DoesNotExist:
            raise Http404("Review not found")

        if action == "hide":
            review.is_visible = False
        elif action == "unhide":
            review.is_visible = True

        review.save()
        return redirect("product_detail", product_id=product_id)

    return render(
        request,
        "product_detail.html",
        {"product": product, "reviews": paginated_reviews, "image_url": image_url},
    )
