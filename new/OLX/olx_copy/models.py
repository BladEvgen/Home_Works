import os
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.core.validators import FileExtensionValidator
from django.db.models.signals import post_save
from django.dispatch import receiver


def user_avatar_path(instance, filename):
    username = instance.user.username
    return f"user_images/{username}/avatar_{username}.{filename.split('.')[-1]}"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(
        upload_to=user_avatar_path, null=True, blank=True, default="png/user.png"
    )

    def get_avatar_url(self):
        return self.avatar.url if self.avatar else None

    def save(self, *args, **kwargs):
        if self.pk:
            old_avatar = UserProfile.objects.get(pk=self.pk).avatar
            if old_avatar and self.avatar != old_avatar:
                if (
                    os.path.isfile(old_avatar.path)
                    and old_avatar.path != "png/user.png"
                ):
                    os.remove(old_avatar.path)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} Profile"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    UserProfile.objects.get_or_create(user=instance)


# @receiver(post_save, sender=User)
# def create_user_profile(sender, instance, created, **kwargs):
#     if created and not hasattr(instance, "userprofile"):
#         UserProfile.objects.create(user=instance)


class CategoryItem(models.Model):
    title = models.CharField(
        max_length=255,
        unique=True,
        db_index=True,
        verbose_name="Наименование",
    )
    slug = models.SlugField(
        max_length=255,
        verbose_name="Ссылка",
        null=False,
        editable=True,
        unique=True,
    )

    class Meta:
        app_label = "olx_copy"
        ordering = ("-title",)
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self) -> str:
        return f"Category(id={self.id}, Title={self.title}, Slug={self.slug})"


class TagItem(models.Model):
    title = models.CharField(
        max_length=255,
        unique=True,
        verbose_name="Наименование",
    )
    slug = models.SlugField(
        max_length=255, verbose_name="Ссылка", null=False, editable=True, unique=True
    )

    class Meta:
        app_label = "olx_copy"
        ordering = ("-title",)
        verbose_name = "Тэг"
        verbose_name_plural = "Тэги"

    def __str__(self) -> str:
        return f"TagItem(id={self.id}, Title={self.title}, Slug={self.slug})"


class Item(models.Model):
    author = models.ForeignKey(
        verbose_name="Автор",
        db_index=True,
        primary_key=False,
        editable=True,
        blank=True,
        null=False,
        default=None,
        to=User,
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=255, verbose_name="Наименование")
    image = models.ImageField(
        upload_to="product_pictures/",
        null=True,
        blank=True,
        editable=True,
        default=None,
        verbose_name="Фото Продукта",
        validators=[
            FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png", "webp"])
        ],
    )
    description = models.TextField(verbose_name="Описание", blank=True)
    price = models.PositiveIntegerField(verbose_name="Цена")
    category = models.ForeignKey(
        "CategoryItem", on_delete=models.CASCADE, verbose_name="Категория"
    )
    is_active = models.BooleanField(default=True, verbose_name="Активность объявления")
    tags = models.ManyToManyField("TagItem", blank=True, verbose_name="Тэги")
    discounted_price = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name="Скидочная цена",
        help_text="Цена со скидкой, если применена",
    )
    discount_percentage = models.FloatField(
        blank=True,
        null=True,
        verbose_name="Процент скидки",
        editable=False,
    )

    def calculate_discount_percentage(self):
        if self.discounted_price is not None and self.price > 0:
            discount = ((self.price - self.discounted_price) / self.price) * 100
            return round(discount, 2)
        return 0.0

    def save(self, *args, **kwargs):
        self.discount_percentage = self.calculate_discount_percentage()
        print(
            f"Price: {self.price}, Discounted Price: {self.discounted_price}, Discount Percentage: {self.discount_percentage}"
        )
        super().save(*args, **kwargs)

    def get_image_url(self):
        return self.image.url if self.image else None

    class Meta:
        app_label = "olx_copy"
        ordering = ("is_active", "title")
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

    def __str__(self):
        status = "Активен" if self.is_active else "Продано"
        return f"Item(id={self.id}, Title={self.title}, Price={self.price}, Category={self.category.title}, Status={status})"


class Review(models.Model):
    product = models.ForeignKey("Item", on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    is_visible = models.BooleanField(default=True)

    created_at = models.DateTimeField(default=timezone.now)


class Vip(models.Model):
    article = models.OneToOneField(
        Item,
        verbose_name="Объявление",
        on_delete=models.CASCADE,
        db_index=True,
    )
    priority = models.IntegerField(
        verbose_name="Приоритет",
        default=5,
    )
    expired = models.DateTimeField(
        verbose_name="дата и время истечения",
        default=timezone.now,
    )

    class Meta:
        app_label = "olx_copy"
        ordering = ("priority", "-expired")
        verbose_name = "Vip объявление"
        verbose_name_plural = "Vip объявления"

    def __str__(self):
        return f"Vip: {self.article.title} ({self.id}) | Priority: {self.priority}"


class ItemRating(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Автор")
    item = models.ForeignKey("Item", on_delete=models.CASCADE, verbose_name="Товар")
    is_like = models.BooleanField(default=True, verbose_name="Понравилось")

    class Meta:
        app_label = "olx_copy"
        ordering = ("-item", "-author")
        verbose_name = "Рейтинг товара"
        verbose_name_plural = "Рейтинги товаров"

    def __str__(self):
        return f"ItemRating(id={self.id}, Author={self.author.username}, Item={self.item.title}, Like={self.is_like})"
