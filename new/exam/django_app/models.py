# models.py

from django.db import models
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.core.validators import FileExtensionValidator


def user_avatar_path(instance, filename):
    username = instance.user.username
    return f"user_images/{username}/avatar_{username}.{filename.split('.')[-1]}"


class UserProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name="Пользователь",
    )
    is_banned = models.BooleanField(default=False, verbose_name="Статус Бана")
    phonenumber = models.CharField(max_length=20, verbose_name="Номер телефона")
    avatar = models.ImageField(
        upload_to=user_avatar_path, null=True, blank=True, verbose_name="Аватар"
    )

    def get_avatar_url(self):
        return self.avatar.url if self.avatar else None

    def __str__(self):
        return f"{self.user.username} Profile"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    UserProfile.objects.get_or_create(user=instance)


def post_image_path(instance, filename):
    username = instance.author.username
    title = instance.title
    return f"post_images/{username}/{title}.{filename.split('.')[-1]}"


class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Автор")
    title = models.CharField(max_length=100, verbose_name="Заголовок", unique=True)
    content = models.TextField(verbose_name="Содержание")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    picture = models.ImageField(
        upload_to=post_image_path,
        null=True,
        blank=True,
        editable=True,
        default=None,
        verbose_name="Фото поста",
        validators=[
            FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png", "webp"])
        ],
    )

    def get_post_url(self) -> str | None:
        return self.picture.url if self.picture else None

    def __str__(self) -> str:
        return f"{self.title } - {self.author}"


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, verbose_name="Пост")
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Автор")
    content = models.TextField(verbose_name="Комментарий")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    is_visible = models.BooleanField(default=True, verbose_name="Видимость")

    def __str__(self) -> str:
        return f"{self.author} - {self.post.title}"


class PostRaiting(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Автор")
    post = models.ForeignKey("Post", on_delete=models.CASCADE, verbose_name="Товар")
    is_like = models.BooleanField(
        default=True,
        verbose_name="Лайк",
        help_text="Статус понравился ли пользователю товар",
    )

    class Meta:
        ordering = ("-post", "-author")
        verbose_name = "Рейтинг Поста"
        verbose_name_plural = "Рейтинги Постов"

    def __str__(self):
        return f"Рэйтинг Поста\n Автор={self.author.username},\n Пост={self.post.title},\n Статус Лайка={self.is_like})"
