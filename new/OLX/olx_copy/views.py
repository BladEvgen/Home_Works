import os
import datetime
from django.http import Http404, HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.files.storage import default_storage
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.urls import reverse
from django.utils.translation import activate
from olx_copy.utils import decorator_error_handler
from olx_copy import models


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
    selected_language = request.COOKIES.get("selected_language", "ENG")
    activate(selected_language)
    return render(
        request,
        "home.html",
        context={
            "categories": categories,
            "vips": vips,
            "selected_language": selected_language,
        },
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
@login_required
def profile(request, username):
    user_profile = get_object_or_404(models.UserProfile, user__username=username)

    selected_language = request.COOKIES.get("selected_language", "ENG")
    activate(selected_language)

    return render(
        request,
        "profile.html",
        context={"user_profile": user_profile, "selected_language": selected_language},
    )


@login_required
def change_data(request, username):
    user_profile = get_object_or_404(models.UserProfile, user=request.user)

    if request.method == "POST":
        email = request.POST.get("email")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")

        request.user.email = email
        request.user.first_name = first_name
        request.user.last_name = last_name
        request.user.save()

        avatar = request.FILES.get("avatar")
        if avatar:
            old_avatar = user_profile.avatar
            if old_avatar:
                if os.path.isfile(old_avatar.path):
                    os.remove(old_avatar.path)

            user_profile.avatar = avatar

        user_profile.save()
        return HttpResponseRedirect(reverse("profile", args=[username]))

    return render(request, "change_data.html", {"user_profile": user_profile})


@decorator_error_handler
def item(request, item_slug: str):
    cat = get_object_or_404(models.CategoryItem, slug=item_slug)
    _items = models.Item.objects.all().filter(is_active=True, category=cat)
    return render(request, "item.html", context={"items": _items})


@login_required
def create_item(request):
    if request.method == "POST":
        title = request.POST.get("name")
        picture = request.FILES.get("picture")
        category_id = request.POST.get("category")
        price = request.POST.get("price")
        description = request.POST.get("description")

        try:
            category = get_object_or_404(models.CategoryItem, id=category_id)

            author = request.user if request.user.is_authenticated else None

            item = models.Item.objects.create(
                title=title,
                image=picture,
                description=description,
                price=price,
                category=category,
                author=author,
            )

            messages.success(request, "Item created successfully.")

        except models.CategoryItem.DoesNotExist:
            messages.error(request, "Selected Category does not exist.")

    categories = models.CategoryItem.objects.all()
    return render(request, "create_product.html", context={"categories": categories})


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
        product = get_object_or_404(models.Item, id=product_id)
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

    if (
        request.method == "POST"
        and request.user.is_authenticated
        and request.user.is_staff
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

    _ratings = models.ItemRating.objects.filter(item=product)
    _total_rating_value = (
        _ratings.filter(is_like=True).count() - _ratings.filter(is_like=False).count()
    )

    _my_rating = None

    if request.user.is_authenticated:
        _my_rating = _ratings.filter(author=request.user).first()

    _is_my_rating = (
        1
        if (_my_rating and _my_rating.is_like)
        else -1
        if (_my_rating and not _my_rating.is_like)
        else 0
    )
    selected_language = request.COOKIES.get("selected_language", "ENG")
    activate(selected_language)

    return render(
        request,
        "product_detail.html",
        {
            "product": product,
            "reviews": paginated_reviews,
            "total_rating_value": _total_rating_value,
            "is_my_rating": _is_my_rating,
            "selected_language": selected_language,
        },
    )


def delete_review(request, product_id):
    if request.method == "POST" and request.user.is_authenticated:
        review_id = request.POST.get("review_id")
        product_id = request.POST.get("product_id")

        try:
            review = get_object_or_404(
                models.Review, id=review_id, product__id=product_id, user=request.user
            )
        except models.Review.DoesNotExist:
            raise Http404("Review not found")

        review.delete()
        return redirect("product_detail", product_id=product_id)

    return HttpResponseForbidden("You don't have permission to perform this action.")


def rating(request, item_id: str, is_like: str):
    author = request.user
    _item = get_object_or_404(models.Item, id=int(item_id))
    _is_like = True if is_like == "1" else False

    try:
        like_obj = models.ItemRating.objects.get(author=author, item=_item)
        if like_obj.is_like == _is_like:
            like_obj.delete()
        else:
            like_obj.is_like = _is_like
            like_obj.save()
    except models.ItemRating.DoesNotExist:
        models.ItemRating.objects.create(author=author, item=_item, is_like=_is_like)

    return redirect(reverse("product_detail", args=(item_id,)))
