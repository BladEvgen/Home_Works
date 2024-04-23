from django_app import models
from rest_framework import serializers


class UserProfileListSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = models.UserProfile
        fields = ["id", "username", "email", "is_banned", "avatar", "full_name"]

    def get_full_name(self, obj):
        if obj.user.first_name and obj.user.last_name:
            return f"{obj.user.first_name} {obj.user.last_name}"
        return None

    def get_email(self, obj):
        if obj.user.email:
            return obj.user.email
        return None


class UserProfileDetailSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    phonenumber = serializers.SerializerMethodField()

    class Meta:
        model = models.UserProfile
        fields = [
            "id",
            "username",
            "email",
            "is_banned",
            "phonenumber",
            "avatar",
            "full_name",
        ]
        extra_kwargs = {
            "phonenumber": {"required": False},
        }

    def get_email(self, obj):
        if obj.user.email:
            return obj.user.email
        return None

    def get_full_name(self, obj):
        if obj.user.first_name and obj.user.last_name:
            return f"{obj.user.first_name} {obj.user.last_name}"
        return None

    def get_phonenumber(self, obj):
        if obj.phonenumber:
            return obj.phonenumber
        return None
