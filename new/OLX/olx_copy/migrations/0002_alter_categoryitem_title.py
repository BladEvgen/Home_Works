# Generated by Django 5.0 on 2024-01-09 17:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('olx_copy', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='categoryitem',
            name='title',
            field=models.CharField(db_index=True, max_length=255, unique=True, verbose_name='Наименование'),
        ),
    ]
