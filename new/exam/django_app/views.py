import os
import datetime

from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.models import User
from django.views.generic import TemplateView, View
from django.core.files.storage import default_storage
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import get_object_or_404, redirect, render
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import Http404, HttpResponseForbidden, HttpResponseRedirect

from rest_framework import generics
from django_app import models, serializers, utils
from rest_framework.pagination import PageNumberPagination


class AboutView(TemplateView):
    template_name = "about.html"


class ProfileView(View):
    template_name = "profile.html"

    def get(self, request, username):
        user = get_object_or_404(User, username=username)
        user_profile, created = models.UserProfile.objects.get_or_create(user=user)

        return render(
            request,
            template_name=self.template_name,
            context={"user_profile": user_profile},
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


def home(request):
    twelve_hours_ago = datetime.datetime.now() - datetime.timedelta(hours=16)
    posts = models.Post.objects.filter(created_at__gte=twelve_hours_ago)
    context = {"posts": posts}
    return render(request, "home.html", context=context)


def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            return render(request, "register.html", {"error": "Passwords do not match"})

        if not utils.password_check(password):
            return render(
                request,
                "register.html",
                {"error": "Password does not meet the required strength criteria."},
            )

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
            return redirect("home")
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


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("home")

    return render(request, "login.html", context={})


@login_required
def user_posts(request):
    posts = models.Post.objects.filter(author=request.user)

    return render(request, "user_posts.html", {"posts": posts})


@login_required
def create_post(request):
    if request.method == "POST":
        title = request.POST.get("name")
        content = request.POST.get("content")
        picture = request.FILES.get("picture")

        try:
            author = request.user if request.user.is_authenticated else None

            post = models.Post.objects.create(
                title=title,
                content=content,
                picture=picture,
                author=author,
            )

            messages.success(request, "Post created successfully.")

            return redirect("post_detail", post_id=post.id)

        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")

    return render(request, "create_post.html")


def post_detail(request, post_id):
    try:
        post = get_object_or_404(models.Post, id=post_id)
    except models.Post.DoesNotExist:
        raise Http404("Product not found")

    reviews = models.Comment.objects.filter(post=post).order_by("-created_at")

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
        comment_id = request.POST.get("review_id")
        action = request.POST.get("action")

        try:
            reviewss = models.Comment.objects.get(id=comment_id, post=post)
        except models.Review.DoesNotExist:
            raise Http404("Review not found")

        if action == "hide":
            reviewss.is_visible = False
        elif action == "unhide":
            reviewss.is_visible = True

        reviewss.save()
        return redirect("post_detail", post_id=post_id)

    _ratings = models.PostRaiting.objects.filter(post=post)
    _total_rating_value = (
        _ratings.filter(is_like=True).count() - _ratings.filter(is_like=False).count()
    )

    _my_rating = None

    if request.user.is_authenticated:
        _my_rating = _ratings.filter(author=request.user).first()

    _is_my_rating = (
        1
        if (_my_rating and _my_rating.is_like)
        else -1 if (_my_rating and not _my_rating.is_like) else 0
    )

    return render(
        request,
        "post_detail.html",
        {
            "post": post,
            "reviews": paginated_reviews,
            "total_rating_value": _total_rating_value,
            "is_my_rating": _is_my_rating,
        },
    )


def add_comment(request, post_id):
    if request.method == "POST":
        post = get_object_or_404(models.Post, id=post_id)
        content = request.POST.get("content")
        models.Comment.objects.create(
            post=post, author=request.user, content=content, is_visible=True
        )
    return redirect("post_detail", post_id=post_id)


def delete_review(request, post_id):
    if request.method == "POST" and request.user.is_authenticated:
        review_id = request.POST.get("review_id")
        post_id = request.POST.get("post_id")

        try:
            review = get_object_or_404(
                models.Comment, id=review_id, post_id=post_id, author=request.user
            )
        except models.Comment.DoesNotExist:
            raise Http404("Review not found")

        review.delete()
        return redirect("post_detail", post_id=post_id)

    return HttpResponseForbidden("You don't have permission to perform this action.")


@login_required
def modify_post(request, post_id):
    post = get_object_or_404(models.Post, id=post_id)

    if request.method == "POST":
        title = request.POST.get("title")

        is_active = True if request.POST.get("is_active", None) else False
        content = request.POST.get("content")
        post.title = title
        post.is_active = is_active
        post.content = content

        new_picture = request.FILES.get("picture")
        if new_picture:
            if post.picture.name and post.picture.name != "nodatafound.png":
                default_storage.delete(post.picture.name)

            picture_extension = new_picture.name.split(".")[-1]
            new_picture_name = f"{post.title.replace(' ', '_')}.{picture_extension}"
            post.picture.save(new_picture_name, new_picture)

        post.save()

        return redirect(reverse("post_detail", args=[post.id]))

    return render(
        request,
        "modify_post.html",
        {
            "post": post,
        },
    )


def raiting(request, post_id: str, is_like: str):
    author = request.user

    _item = get_object_or_404(models.Post, id=int(post_id))

    _is_like = True if is_like == "1" else False

    try:
        rating_obj = models.PostRaiting.objects.get(author=author, post=_item)

        if rating_obj.is_like == _is_like:
            rating_obj.delete()
        else:
            rating_obj.is_like = _is_like
            rating_obj.save()
    except models.PostRaiting.DoesNotExist:
        models.PostRaiting.objects.create(author=author, post=_item, is_like=_is_like)

    return redirect(reverse("post_detail", args=(post_id,)))


class UserListCreateAPIView(generics.ListCreateAPIView):
    queryset = models.UserProfile.objects.all()
    serializer_class = serializers.UserProfileListSerializer
    pagination_class = PageNumberPagination


class UserRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.UserProfile.objects.all()
    serializer_class = serializers.UserProfileDetailSerializer
