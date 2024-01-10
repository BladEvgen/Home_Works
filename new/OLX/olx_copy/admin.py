from django.contrib import admin
from .models import CategoryItem, TagItem, Item

# Register your models here.
admin.site.register(Item)
admin.site.register(CategoryItem)
admin.site.register(TagItem)
