# Generated by Django 5.0.3 on 2024-03-10 17:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('django_app', '0002_userextend_active'),
    ]

    operations = [
        migrations.RenameField(
            model_name='userextend',
            old_name='active',
            new_name='is_active',
        ),
    ]
