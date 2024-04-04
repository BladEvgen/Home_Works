from django.db import models
from django.utils import timezone
from django.db.models.signals import pre_save
from django.dispatch import receiver


class Category(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название")
    slug = models.SlugField(unique=True, verbose_name="Слаг (ссылка латиницей)")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"


class Clothes(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название")
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, verbose_name="Категория"
    )
    wearing_period = models.IntegerField(
        default=0, verbose_name="Период ношения в днях"
    )
    description = models.TextField(blank=True, null=True, verbose_name="Описание")

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = "Предмет одежды"
        verbose_name_plural = "Предметы одежды"


class Person(models.Model):
    first_name = models.CharField(max_length=100, verbose_name="Имя")
    last_name = models.CharField(max_length=100, db_index=True, verbose_name="Фамилия")
    patronymic = models.CharField(
        max_length=100, verbose_name="Отчество", blank=True, null=True
    )
    tabel_num = models.CharField(
        unique=True, max_length=24, db_index=True, verbose_name="Табельный номер"
    )

    class Meta:
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"

    def __str__(self):
        return f"{self.tabel_num} - {self.last_name}"


class ClothesUser(models.Model):
    clothes = models.ForeignKey(
        Clothes,
        on_delete=models.CASCADE,
        verbose_name="Предмет одежды",
        null=True,
        blank=True,
    )
    person = models.ForeignKey(
        Person, on_delete=models.CASCADE, verbose_name="Пользователь"
    )
    date_started_wearing = models.DateField(verbose_name="Дата начала ношения")
    date_ended_wearing = models.DateField(
        verbose_name="Дата окончания ношения", blank=True, null=True
    )

    class Meta:
        verbose_name = "Экипировка пльзователя"
        verbose_name_plural = "Экипировки пользователей"

    def __str__(self) -> str:
        return f"{self.clothes.name} -- Табельнй номер: {self.person.tabel_num}; ФИО: {self.person.first_name} {self.person.last_name}"

    def get_remaining_days(self):
        if self.date_ended_wearing:
            remaining_days = (self.date_ended_wearing - timezone.now().date()).days
            return remaining_days
        return 0

    def save(self, *args, **kwargs) -> None:
        if not self.date_ended_wearing:
            self.date_ended_wearing = self.date_started_wearing + timezone.timedelta(
                days=self.clothes.wearing_period
            )
        super().save(*args, **kwargs)


@receiver(pre_save, sender=ClothesUser)
def calculate_date_ended_wearing(sender, instance, **kwargs):
    if not instance.date_ended_wearing:
        instance.date_ended_wearing = (
            instance.date_started_wearing
            + timezone.timedelta(days=instance.clothes.wearing_period)
        )
