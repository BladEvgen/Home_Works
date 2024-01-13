from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    expiration_date = models.DateField()
    picture = models.ImageField(upload_to="product_images/", null=True, blank=True)
    qr_code = models.ImageField(upload_to="qr_codes/", null=True, blank=True)
