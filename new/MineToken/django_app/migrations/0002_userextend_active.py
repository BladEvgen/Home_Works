# Generated by Django 5.0.3 on 2024-03-10 16:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userextend',
            name='active',
            field=models.BooleanField(default=True),
        ),
    ]