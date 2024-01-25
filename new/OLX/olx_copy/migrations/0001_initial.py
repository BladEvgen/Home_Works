# Generated by Django 5.0.1 on 2024-01-25 09:51

import django.core.validators
import django.db.models.deletion
import django.utils.timezone
import olx_copy.models
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CategoryItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(db_index=True, max_length=255, unique=True, verbose_name='Наименование')),
                ('slug', models.SlugField(max_length=255, unique=True, verbose_name='Ссылка')),
            ],
            options={
                'verbose_name': 'Категория',
                'verbose_name_plural': 'Категории',
                'ordering': ('-title',),
            },
        ),
        migrations.CreateModel(
            name='TagItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, unique=True, verbose_name='Наименование')),
                ('slug', models.SlugField(max_length=255, unique=True, verbose_name='Ссылка')),
            ],
            options={
                'verbose_name': 'Тэг',
                'verbose_name_plural': 'Тэги',
                'ordering': ('-title',),
            },
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='Наименование')),
                ('image', models.ImageField(blank=True, default=None, null=True, upload_to='product_pictures/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp'])], verbose_name='Фото Продукта')),
                ('description', models.TextField(blank=True, verbose_name='Описание')),
                ('price', models.PositiveIntegerField(verbose_name='Цена')),
                ('is_active', models.BooleanField(default=True, verbose_name='Активность объявления')),
                ('discounted_price', models.PositiveIntegerField(blank=True, help_text='Цена со скидкой, если применена', null=True, verbose_name='Скидочная цена')),
                ('discount_percentage', models.FloatField(blank=True, editable=False, null=True, verbose_name='Процент скидки')),
                ('author', models.ForeignKey(blank=True, default=None, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Автор')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='olx_copy.categoryitem', verbose_name='Категория')),
                ('tags', models.ManyToManyField(blank=True, to='olx_copy.tagitem', verbose_name='Тэги')),
            ],
            options={
                'verbose_name': 'Товар',
                'verbose_name_plural': 'Товары',
                'ordering': ('is_active', 'title'),
            },
        ),
        migrations.CreateModel(
            name='ItemRating',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_like', models.BooleanField(default=True, verbose_name='Понравилось')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Автор')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='olx_copy.item', verbose_name='Товар')),
            ],
            options={
                'verbose_name': 'Рейтинг товара',
                'verbose_name_plural': 'Рейтинги товаров',
                'ordering': ('-item', '-author'),
            },
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('is_visible', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='olx_copy.item')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, db_index=True, default='', max_length=255, verbose_name='Наименование')),
                ('slug', models.SlugField(default='', max_length=300, unique=True, verbose_name='Ссылка')),
                ('token', models.CharField(blank=True, db_index=True, default=uuid.uuid4, max_length=255, null=True, unique=True, verbose_name='Токен')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, editable=False, verbose_name='Дата Создания')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='olx_copy.item')),
                ('user_opponent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rooms_opponent', to=settings.AUTH_USER_MODEL, verbose_name='Ответчик')),
                ('user_started', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rooms_started', to=settings.AUTH_USER_MODEL, verbose_name='Вопрощатель')),
            ],
            options={
                'ordering': ('-slug', '-name'),
            },
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField(default='', verbose_name='Текст сообщения')),
                ('date_added', models.DateTimeField(db_index=True, default=django.utils.timezone.now, verbose_name='дата и время добавления')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to=settings.AUTH_USER_MODEL, verbose_name='Автор')),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='olx_copy.room', verbose_name='Комната')),
            ],
            options={
                'ordering': ('-date_added', '-room'),
            },
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('avatar', models.ImageField(blank=True, null=True, upload_to=olx_copy.models.user_avatar_path)),
                ('is_banned', models.BooleanField(default=False)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Vip',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('priority', models.IntegerField(default=5, verbose_name='Приоритет')),
                ('expired', models.DateTimeField(default=django.utils.timezone.now, verbose_name='дата и время истечения')),
                ('article', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='olx_copy.item', verbose_name='Объявление')),
            ],
            options={
                'verbose_name': 'Vip объявление',
                'verbose_name_plural': 'Vip объявления',
                'ordering': ('priority', '-expired'),
            },
        ),
    ]
