# Generated by Django 5.0.1 on 2024-01-25 11:13

import django.db.models.deletion
import django.utils.timezone
import olx_copy.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('olx_copy', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='message',
            options={'ordering': ('-date_added', '-room'), 'verbose_name': 'Сообщение', 'verbose_name_plural': 'Сообщения'},
        ),
        migrations.AlterModelOptions(
            name='review',
            options={'verbose_name': 'Отзыв', 'verbose_name_plural': 'Отзывы'},
        ),
        migrations.AlterModelOptions(
            name='room',
            options={'ordering': ('-slug', '-name'), 'verbose_name': 'Чат', 'verbose_name_plural': 'Чаты'},
        ),
        migrations.AlterModelOptions(
            name='userprofile',
            options={'verbose_name': 'Профиль пользователя', 'verbose_name_plural': 'Профили пользователей'},
        ),
        migrations.AlterField(
            model_name='itemrating',
            name='is_like',
            field=models.BooleanField(default=True, help_text='Статус понравился ли пользователю товар', verbose_name='Лайк'),
        ),
        migrations.AlterField(
            model_name='message',
            name='date_added',
            field=models.DateTimeField(db_index=True, default=django.utils.timezone.now, verbose_name='Дата и Время Добавления'),
        ),
        migrations.AlterField(
            model_name='review',
            name='content',
            field=models.TextField(verbose_name='Комментарий'),
        ),
        migrations.AlterField(
            model_name='review',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='Дата Создания'),
        ),
        migrations.AlterField(
            model_name='review',
            name='is_visible',
            field=models.BooleanField(default=True, verbose_name='Видимость'),
        ),
        migrations.AlterField(
            model_name='review',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='olx_copy.item', verbose_name='Название товара'),
        ),
        migrations.AlterField(
            model_name='review',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'),
        ),
        migrations.AlterField(
            model_name='room',
            name='item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='olx_copy.item', verbose_name='Товар о котором идет речь'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='avatar',
            field=models.ImageField(blank=True, null=True, upload_to=olx_copy.models.user_avatar_path, verbose_name='Аватар'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='is_banned',
            field=models.BooleanField(default=False, verbose_name='Статус Бана'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'),
        ),
        migrations.AlterField(
            model_name='vip',
            name='expired',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='Дата и Время Истечения'),
        ),
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField(default=1, verbose_name='Колличество')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='olx_copy.item', verbose_name='Товар')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='olx_copy.userprofile', verbose_name='Пользователь')),
            ],
        ),
    ]