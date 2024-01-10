from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


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
    title = models.CharField(
        verbose_name="Наименование",
        unique=False,
        editable=True,
        blank=True,
        null=False,
        max_length=255,
    )
    description = models.TextField(
        verbose_name="Описание", unique=False, editable=True, blank=True
    )
    price = models.PositiveIntegerField(
        verbose_name="Цена", unique=False, blank=True, null=False, primary_key=False
    )
    category = models.ForeignKey(
        verbose_name="Категория",
        db_index=True,
        primary_key=False,
        unique=False,
        editable=True,
        max_length=100,
        to=CategoryItem,
        on_delete=models.CASCADE,
    )
    is_active = models.BooleanField(
        verbose_name="Активность объявления", null=False, default=True
    )
    tags = models.ManyToManyField(
        verbose_name="Тэги",
        to=TagItem,
        max_length=100,
        blank=True,
        unique=False,
        primary_key=False,
        editable=True,
    )

    class Meta:
        app_label = "olx_copy"
        ordering = ("is_active", "-title")
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

    def __str__(self) -> str:
        status = "Активен" if self.is_active else "Продано"
        return f"Item(id={self.id}, Title={self.title}, Price={self.price}, Category={self.category.title}, Status={status})"
