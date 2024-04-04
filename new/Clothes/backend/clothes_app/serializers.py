from rest_framework import serializers
from clothes_app import models


class ClothesUserSerializer(serializers.ModelSerializer):
    tabel_id = serializers.SerializerMethodField()
    person_full_name = serializers.SerializerMethodField()
    clothes_category = serializers.SerializerMethodField()
    clothes_name = serializers.SerializerMethodField()
    remaining_days = serializers.SerializerMethodField()

    class Meta:
        model = models.ClothesUser
        fields = (
            "tabel_id",
            "person_full_name",
            "clothes_category",
            "clothes_name",
            "remaining_days",
        )

    def get_tabel_id(self, obj):
        return obj.person.tabel_num

    def get_person_full_name(self, obj):
        if obj.person.patronymic is None:
            return f"{obj.person.last_name} {obj.person.first_name}"
        return f"{obj.person.last_name} {obj.person.first_name} {obj.person.patronymic}"

    def get_clothes_category(self, obj):
        return obj.clothes.category.name

    def get_clothes_name(self, obj):
        return obj.clothes.name

    def get_remaining_days(self, obj):
        return obj.get_remaining_days()
