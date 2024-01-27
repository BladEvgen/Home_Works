import os
import uuid
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.core.validators import FileExtensionValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify


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
    avatar = models.ImageField(
        upload_to=user_avatar_path, null=True, blank=True, verbose_name="Аватар"
    )
    is_banned = models.BooleanField(default=False, verbose_name="Статус Бана")
    phonenumber = models.CharField(max_length=20, verbose_name="Номер телефона")
    address = models.TextField(verbose_name="Адрес доставки")

    def get_avatar_url(self):
        return self.avatar.url if self.avatar else None

    def ban_user(self):
        self.user.is_active = False
        self.user.save()

    def unban_user(self):
        self.user.is_active = True
        self.user.save()

    def delete_user(self):
        self.user.delete()

    def get_avatar_url(self):
        return self.avatar.url if self.avatar else None

    def check_access(self, action_slug: str = ""):
        try:
            user: User = self.user
            action: Action = Action.objects.get(slug=action_slug)
            intersections = GroupExtend.objects.filter(users=user, actions=action)
            if len(intersections) > 0:
                return True
            return False
        except Exception as error:
            print("error check_access: ", error)
            return False

    def get_actions(self):
        try:
            user: User = self.user
            group_extends = GroupExtend.objects.filter(users=user)
            actions = Action.objects.filter(groupextend__in=group_extends).distinct()

            return actions
        except GroupExtend.DoesNotExist:
            return []

    def has_action(self, action_slug: str):
        return self.get_actions().filter(slug=action_slug).exists()

    def __str__(self):
        return f"{self.user.username} Profile"

    class Meta:
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    UserProfile.objects.get_or_create(user=instance)


class Action(models.Model):
    slug = models.SlugField(
        verbose_name="Ссылка",
        max_length=500,
        unique=True,
    )
    description = models.TextField(
        verbose_name="Описание",
        default="",
    )

    class Meta:
        app_label = "auth"
        ordering = ("slug",)
        verbose_name = "Действие"
        verbose_name_plural = "Действия"

    def __str__(self):
        return f"Действие: {self.slug} - {self.description[:50]}"


class GroupExtend(models.Model):
    name = models.CharField(
        verbose_name="Название группы",
        max_length=300,
        unique=True,
    )
    users = models.ManyToManyField(
        verbose_name="Пользователи принадлежащие к группе",
        to=User,
    )
    actions = models.ManyToManyField(
        verbose_name="Возможности доступные этой группе",
        to=Action,
    )

    class Meta:
        app_label = "auth"
        ordering = ("name",)
        verbose_name = "Группа"
        verbose_name_plural = "Группы"

    def __str__(self):
        return f"Группа: {self.name}"

    def has_action(self, action_slug: str):
        return self.actions.filter(slug=action_slug).exists()


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
        return f"Категория(id={self.id}, Название={self.title}, Ссылка={self.slug})"


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
        return f"Тэг(id={self.id}, Название={self.title}, Ссылка={self.slug})"


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
            f"Цена: {self.price}, Скидоная Цена: {self.discounted_price}, Процентаж Скидки: {self.discount_percentage}"
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
        return f"Товар(id={self.id}, Название={self.title}, Цена={self.price}, Категория={self.category.title}, Статус={status})"


class Cart(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="Пользователь"
    )
    item = models.ForeignKey(Item, on_delete=models.CASCADE, verbose_name="Товар")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Количество")

    def get_total_price(self):
        return (
            self.item.discounted_price
            if self.item.discounted_price
            else self.item.price
        )

    def calculate_item_total(self):
        return self.quantity * self.get_total_price()

    class Meta:
        verbose_name = "Элемент корзины"
        verbose_name_plural = "Элементы корзины"


class Review(models.Model):
    product = models.ForeignKey(
        "Item", on_delete=models.CASCADE, verbose_name="Название товара"
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="Пользователь"
    )
    content = models.TextField(verbose_name="Комментарий")
    is_visible = models.BooleanField(default=True, verbose_name="Видимость")

    created_at = models.DateTimeField(
        default=timezone.now, verbose_name="Дата Создания"
    )

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"


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
        verbose_name="Дата и Время Истечения",
        default=timezone.now,
    )

    class Meta:
        app_label = "olx_copy"
        ordering = ("priority", "-expired")
        verbose_name = "Vip объявление"
        verbose_name_plural = "Vip объявления"

    def __str__(self):
        return f"Vip: {self.article.title} ({self.id}) | Приоритет: {self.priority}"


class ItemRating(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Автор")
    item = models.ForeignKey("Item", on_delete=models.CASCADE, verbose_name="Товар")
    is_like = models.BooleanField(
        default=True,
        verbose_name="Лайк",
        help_text="Статус понравился ли пользователю товар",
    )

    class Meta:
        app_label = "olx_copy"
        ordering = ("-item", "-author")
        verbose_name = "Рейтинг товара"
        verbose_name_plural = "Рейтинги товаров"

    def __str__(self):
        return f"Рэйтинг Товара (id={self.id},\n Автор={self.author.username},\n Товар={self.item.title},\n Статус Лайка={self.is_like})"


# TODO PRIVATE CHAT


class RoomManager(models.Manager):
    def with_messages(self):
        return self.prefetch_related("messages")


class Room(models.Model):
    name = models.CharField(
        verbose_name="Наименование",
        max_length=255,
        db_index=True,
        unique=False,
        editable=True,
        blank=True,
        null=False,
        default="",
    )
    slug = models.SlugField(
        verbose_name="Ссылка",
        max_length=300,
        db_index=True,
        unique=True,
        editable=True,
        blank=False,
        null=False,
        default="",
    )

    token = models.CharField(
        verbose_name="Токен",
        max_length=255,
        db_index=True,
        unique=True,
        blank=True,
        null=True,
        default=uuid.uuid4,
    )

    user_started = models.ForeignKey(
        User,
        verbose_name="Вопрощатель",
        related_name="rooms_started",
        on_delete=models.CASCADE,
    )

    user_opponent = models.ForeignKey(
        User,
        verbose_name="Ответчик",
        related_name="rooms_opponent",
        on_delete=models.CASCADE,
    )

    item = models.ForeignKey(
        Item, on_delete=models.CASCADE, verbose_name="Товар о котором идет речь"
    )

    created_at = models.DateTimeField(
        verbose_name="Дата Создания",
        editable=False,
        default=timezone.now,
    )
    objects = RoomManager()

    def get_opponent_username(self, user):
        return (
            self.user_opponent.username
            if user == self.user_started
            else self.user_started.username
        )

    def is_valid_token(self, provided_token):
        return self.token == provided_token

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = f"room_id_{str(uuid.uuid4())[:8]}"
        if not self.token:
            self.token = str(uuid.uuid4())
        super(Room, self).save(*args, **kwargs)

    class Meta:
        verbose_name = "Чат"
        verbose_name_plural = "Чаты"
        app_label = "olx_copy"
        ordering = ("-slug", "-name")

    def __str__(self):
        return f"Room: {self.name} ({self.slug})"


@receiver(post_save, sender=Room)
def create_slug_for_room(sender, instance, created, **kwargs):
    if created and not instance.slug:
        instance.slug = f"{slugify(instance.name)}-{uuid.uuid4().hex[:8]}"
        instance.save()


@receiver(post_save, sender=Room)
def create_token_for_existing_rooms(sender, instance, **kwargs):
    if not instance.token:
        instance.token = str(uuid.uuid4())
        instance.save()


class Message(models.Model):
    user = models.ForeignKey(
        verbose_name="Автор",
        to=User,
        on_delete=models.CASCADE,
        related_name="messages",
    )
    room = models.ForeignKey(
        verbose_name="Комната",
        to=Room,
        on_delete=models.CASCADE,
        related_name="messages",
    )
    content = models.TextField(
        verbose_name="Текст сообщения",
        default="",
        db_index=False,
        unique=False,
        editable=True,
        blank=False,
        null=False,
    )
    date_added = models.DateTimeField(
        verbose_name="Дата и Время Добавления",
        default=timezone.now,
        db_index=True,
    )

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"
        app_label = "olx_copy"
        ordering = ("-date_added", "-room")

    def __str__(self):
        truncated_content = (
            self.content[:30] + "..." if len(self.content) > 30 else self.content
        )
        return f"Сообщение от {self.user.username} в {self.room.name}: {truncated_content} ({self.date_added})"
