from django.db import models
from django.contrib.auth.models import User


class Token(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=128, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)


class UserExtend(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
