# Generated by Django 5.0 on 2023-12-23 15:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('django_app', '0002_review_visible_to_staff'),
    ]

    operations = [
        migrations.RenameField(
            model_name='review',
            old_name='status',
            new_name='is_visible',
        ),
        migrations.RemoveField(
            model_name='review',
            name='visible_to_staff',
        ),
    ]