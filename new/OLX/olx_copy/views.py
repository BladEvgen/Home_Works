import os
import datetime
from django.http import (
    Http404,
    HttpResponseRedirect,
    HttpResponseForbidden,
    JsonResponse,
)
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import (
    TemplateView,
    View,
    ListView,
    DetailView,
    DeleteView,
    CreateView,
)
from django.contrib import messages
from django.core.files.storage import default_storage
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.urls import reverse
from django.utils.translation import activate
from olx_copy.utils import decorator_error_handler
from olx_copy import models
from django.db.models import Q


class AboutView(TemplateView):
    template_name = "about.html"


def about(request):
    return render(request, "about.html", context={})


@decorator_error_handler
def search(request):
    if request.method == "POST":
        _search = request.POST.get("search", "")
        _items = models.Item.objects.all().filter(
            is_active=True, title__icontains=_search
        )
        return render(
            request, "item.html", context={"items": _items, "search": _search}
        )


@decorator_error_handler
def home(request):
    categories = models.CategoryItem.objects.all()
    vips = (
        models.Vip.objects.all()
        .filter(
            expired__gt=datetime.datetime.now(),
            article__is_active=True,
        )
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


class ProfileView(View):
    template_name = "profile.html"

    def get(self, request, username):
        user = get_object_or_404(User, username=username)
        user_profile, created = models.UserProfile.objects.get_or_create(user=user)

        selected_language = request.COOKIES.get("selected_language", "ENG")
        activate(selected_language)

        return render(
            request,
            template_name=self.template_name,
            context={
                "user_profile": user_profile,
                "selected_language": selected_language,
            },
        )

    def post(self, request, username):
        user = get_object_or_404(User, username=username)
        user_profile, created = models.UserProfile.objects.get_or_create(user=user)

        avatar = request.FILES.get("avatar", None)
        if avatar:
            user_profile.avatar = avatar
            user_profile.save()

        return render(
            request,
            template_name=self.template_name,
            context={"user_profile": user_profile},
        )


@login_required
def user_items(request):
    items = models.Item.objects.filter(author=request.user)

    return render(request, "user_items.html", {"items": items})


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

            if old_avatar and os.path.basename(old_avatar.name) == "user.png":
                pass
            else:
                if old_avatar and os.path.isfile(old_avatar.path):
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

            return redirect("product_detail", product_id=item.id)

        except models.CategoryItem.DoesNotExist:
            messages.error(request, "Selected Category does not exist.")

    categories = models.CategoryItem.objects.all()
    return render(request, "create_product.html", context={"categories": categories})


@login_required
def modify_item(request, item_id):
    item = get_object_or_404(models.Item, id=item_id)
    categories = models.CategoryItem.objects.all()
    tags = models.TagItem.objects.all()

    if request.method == "POST":
        title = request.POST.get("title")
        original_price = request.POST.get("original_price")
        discounted_price = request.POST.get("discounted_price")
        category_id = request.POST.get("category")
        tags_ids = request.POST.getlist("tags")
        is_active = True if request.POST.get("is_active", None) else False

        item.title = title
        item.price = int(original_price)
        item.discounted_price = (
            int(discounted_price)
            if discounted_price and discounted_price.strip()
            else None
        )
        item.category = models.CategoryItem.objects.get(id=category_id)
        item.tags.set(models.TagItem.objects.filter(id__in=tags_ids))
        item.is_active = is_active

        new_image = request.FILES.get("image")
        if new_image:
            if item.image.name != "nodatafound.png":
                default_storage.delete(item.image.name)

            image_extension = new_image.name.split(".")[-1]
            new_image_name = f"{item.title.replace(' ', '_')}.{image_extension}"
            item.image.save(new_image_name, new_image)

        item.save()

        return redirect(reverse("product_detail", args=[item.id]))

    return render(
        request,
        "modify_item.html",
        {"item": item, "categories": categories, "tags": tags},
    )


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


def chat(request):
    sort = request.GET.get("sort", "desc")
    user_rooms = models.Room.objects.filter(
        Q(user_started=request.user) | Q(user_opponent=request.user)
    ).distinct()

    if sort == "asc":
        user_rooms = user_rooms.order_by("created_at")
    else:
        user_rooms = user_rooms.order_by("-created_at")

    room_data = []
    for room in user_rooms:
        opponent_username = (
            room.user_opponent.username
            if request.user == room.user_started
            else room.user_started.username
        )
        room_data.append(
            {
                "room": room,
                "opponent_username": opponent_username,
            }
        )

    selected_language = request.COOKIES.get("selected_language", "ENG")
    activate(selected_language)

    return render(
        request,
        "ChatPage.html",
        context={
            "room_data": room_data,
            "current_user": request.user,
            "selected_language": selected_language,
            "sort": sort,
        },
    )


@login_required
def room(request, room_slug: str, token: str):
    _room = get_object_or_404(models.Room, slug=room_slug)

    if not _room.is_valid_token(token):
        return HttpResponseForbidden("Invalid token for this room")

    _messages = models.Message.objects.filter(room=_room)[::-1]
    selected_language = request.COOKIES.get("selected_language", "ENG")
    activate(selected_language)
    return render(
        request,
        "RoomPage.html",
        context={
            "room": _room,
            "messages": _messages,
            "selected_language": selected_language,
        },
    )


@csrf_exempt
def create_chat_room(request):
    try:
        if request.method == "POST" and request.user.is_authenticated:
            item_id = request.POST.get("item_id")

            try:
                item = get_object_or_404(models.Item, pk=item_id)
            except models.Item.DoesNotExist:
                print(f"Item with ID {item_id} not found")
                return JsonResponse({"success": False, "error": "Item not found"})

            user_opponent = item.author

            existing_room = models.Room.objects.filter(
                Q(user_started=request.user, user_opponent=user_opponent, item=item)
                | Q(user_opponent=request.user, user_started=user_opponent, item=item)
            ).first()

            print(f"\nItem ID: {item_id} \nExisting Room: {existing_room}\n")

            if existing_room:
                room_slug = existing_room.slug
                room_token = existing_room.token
            else:
                room = models.Room(
                    user_started=request.user, user_opponent=user_opponent, item=item
                )
                room.save()
                room_slug = room.slug
                room_token = room.token

            print(f"Room Slug: {room_slug}\nRoom Token: {room_token}")

            print(f"Request user: {request.user.username}")

            if room_slug:
                room_url = reverse("room", args=[room_slug, room_token])
                print(f"\nRoom created - URL: {room_url}")
                return JsonResponse({"success": True, "room_url": room_url})
            else:
                print("\nEmpty room_slug encountered\n")
                return JsonResponse({"success": False, "error": "Empty room_slug"})

    except Exception as e:
        print("Exception in create_chat_room:", str(e))
        return JsonResponse({"success": False, "error": str(e)})


def check_access_slug(slug: str, redirect_url: str = "home"):
    def check_access(func):
        def wrapper(*args, **kwargs):
            user: User = args[0].user
            if not user.is_authenticated:
                return redirect(reverse(redirect_url))

            try:
                profile: models.UserProfile = models.UserProfile.objects.get(user=user)
            except models.UserProfile.DoesNotExist:
                return HttpResponseForbidden("Invalid Rights for YOU")

            is_access: bool = profile.check_access(slug)

            if not is_access:
                return redirect(reverse(redirect_url))

            # TODO VIEW
            res = func(*args, **kwargs)
            return res

        return wrapper

    return check_access



@check_access_slug(slug="UsersModeratePage_view")
def moderate_users(request):
    users = User.objects.all()
    return render(request, "ModerateUsers.html", context={"users": users})


@check_access_slug(slug="UsersModeratePage_ban")
def moderate_ban_users(request):
    return render(request, "ModerateUsers.html")


@check_access_slug(slug="UsersModeratePage_delete")
def moderate_delete_users(request):
    return render(request, "ModerateUsers.html")
