# Generated by Django 5.0 on 2024-01-11 16:04

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('olx_copy', '0005_vip'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='item',
            options={'ordering': ('is_active', 'title'), 'verbose_name': 'Товар', 'verbose_name_plural': 'Товары'},
        ),
        migrations.AlterField(
            model_name='item',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='olx_copy.categoryitem', verbose_name='Категория'),
        ),
        migrations.AlterField(
            model_name='item',
            name='price',
            field=models.PositiveIntegerField(verbose_name='Цена'),
        ),
        migrations.AlterField(
            model_name='item',
            name='tags',
            field=models.ManyToManyField(blank=True, to='olx_copy.tagitem', verbose_name='Тэги'),
        ),
        migrations.AlterField(
            model_name='item',
            name='title',
            field=models.CharField(max_length=255, verbose_name='Наименование'),
        ),
        migrations.CreateModel(
            name='ItemRating',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_like', models.BooleanField(default=True, verbose_name='Лайк или не лайк')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Автор')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='olx_copy.item', verbose_name='Товар')),
            ],
            options={
                'verbose_name': 'Рейтинг товара',
                'verbose_name_plural': 'Рейтинги товаров',
                'ordering': ('-item', '-author'),
            },
        ),
    ]
