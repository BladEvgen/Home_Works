from django_app import models
from django.contrib import admin

admin.site.register(models.UserProfile)

admin.site.register(models.Post)
admin.site.register(models.Comment)
