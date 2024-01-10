from django.urls import path
from olx_copy import views


urlpatterns = [
    path("", views.home, name=""),
    path("home", views.home, name="home"),
    path("index", views.home, name="home"),
    path("about", views.about, name="about"),
    path("register", views.register, name="register"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("profile/<str:username>/", views.profile, name="profile"),
    path("item/<str:item_slug>/", views.item, name="item"),
    path("category/<str:slug_name>/", views.items, name="items"),
    path("category", views.category, name="category"),
]
