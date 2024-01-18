from django.contrib import admin
from .models import CategoryItem, TagItem, Item, Review, Vip, ItemRating, UserProfile, Room, RoomManager

# Register your models here.
admin.site.register(Item)
admin.site.register(CategoryItem)
admin.site.register(TagItem)
admin.site.register(Review)
admin.site.register(Vip)
admin.site.register(ItemRating)
admin.site.register(UserProfile)
admin.site.register(Room)