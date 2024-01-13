from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django_app import views

urlpatterns = [
    path("", views.home, name=""),
    path("home", views.home, name="home"),
    path("index", views.home, name="index"),
    path("create/", views.create_product, name="create_product"),
    path("product/<int:product_id>/", views.product_detail, name="product_detail"),
    path("register", views.register, name="register"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("profile/<str:username>/", views.profile, name="profile"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
