from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from olx_copy import views
from olx_copy import views_a

urlpatterns = [
    path("", views.home, name=""),
    path("home/", views.home, name="home"),
    path("index/", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("profile/<str:username>/", views.profile, name="profile"),
    path("item/<str:item_slug>/", views.item, name="item"),
    path("create_item/", views.create_item, name="create_item"),
    path("search/", views.search, name="search"),
    path("add_review/<int:product_id>/", views.add_review, name="add_review"),
    path(
        "product_detail/<int:product_id>/", views.product_detail, name="product_detail"
    ),
    path("rating/<str:item_id>/<str:is_like>/", views.rating, name="rating"),
    path("profile/<str:username>/change_data/", views.change_data, name="change_data"),
    path("delete_review/<int:product_id>/", views.delete_review, name="delete_review"),
    # TODO CHAT WITH TOKEN
    path("chat/", views.chat, name="chat"),
    path("chat/<slug:room_slug>/<str:token>/", views.room, name="room"),
    path("create_chat_room/", views.create_chat_room, name="create_chat_room"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


websocket_urlpatterns = [
    path("ws/chat/<slug:room_name>/", views_a.ChatConsumer.as_asgi())
]
