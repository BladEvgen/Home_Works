from django_app import models
from django.contrib import admin


@admin.register(models.UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "is_banned", "phonenumber", "get_avatar")
    list_filter = ("is_banned",)
    search_fields = ("user__username", "phonenumber")
    ordering = ("user__username",)
    list_editable = ("is_banned",)
    readonly_fields = ("get_avatar",)

    def get_avatar(self, obj):
        return obj.avatar.url if obj.avatar else None

    get_avatar.short_description = "Аватар"


@admin.register(models.Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "created_at", "get_post_image", "created_at")
    list_filter = ("author", "created_at")
    search_fields = ("title", "author__username")
    ordering = ("-created_at",)
    readonly_fields = ("get_post_image", "content", "author", "title")

    def get_post_image(self, obj):
        return obj.picture.url if obj.picture else None

    get_post_image.short_description = "Фото поста"


@admin.register(models.Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("author", "post", "created_at", "content")
    list_filter = ("author", "post", "created_at")
    search_fields = ("author__username", "post__title", "content")
    ordering = ("-created_at",)
    readonly_fields = ("content", "author", "post")


@admin.register(models.PostRaiting)
class PostRaitingAdmin(admin.ModelAdmin):
    list_display = ("author", "post", "is_like")
    list_filter = ("author", "post", "is_like")
    search_fields = ("author__username", "post__title")
    ordering = ("post", "author")
