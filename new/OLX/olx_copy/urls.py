from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
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
    path("search", views.search, name="search"),
    path("add_review/<int:product_id>/", views.add_review, name="add_review"),
    path(
        "product_detail/<int:product_id>/", views.product_detail, name="product_detail"
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
