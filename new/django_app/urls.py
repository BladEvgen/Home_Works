"""
django_app/urls.py - Маршрутизация на приложения
"""
from django.urls import path
from django_app import views

urlpatterns = [
    #    url    view(def)   name
    path("", views.home, name=""),
    path("home", views.home, name="home"),
    path("index", views.home, name="index"),
    path("about", views.about, name="about"),
    path("login", views.login, name="login"),
    path("register", views.register, name="register"),
    path("profile/<str:username>/", views.profile, name="profile"),
    path("product_list", views.product_list, name="product_list"),
]
