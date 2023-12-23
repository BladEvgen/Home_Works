from django.db import models
from django.contrib.auth.models import User


class Review(models.Model):
    product = models.ForeignKey("Product", on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    status = models.BooleanField(default=True)
    visible_to_staff = models.BooleanField(default=True)


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name
