"""
django_app/urls.py - Маршрутизация на приложения
"""
from django.urls import path
from django_app import views

urlpatterns = [
    #    url    view(def)   name
    path("", views.home, name=""),
    path("home", views.home, name="home"),
    path("about", views.about, name="about"),
    path("index", views.home, name="index"),
    path("login", views.login_view, name="login"),
    path("register", views.register, name="register"),
    path("logout", views.logout_view, name="logout"),
    path("profile/<str:username>/", views.profile, name="profile"),
    path("price_list", views.price_list, name="price_list"),
]
