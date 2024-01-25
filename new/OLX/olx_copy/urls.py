from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from olx_copy import views
from olx_copy import views_a

urlpatterns = [
    # * Home and User Authentication
    path("", views.home, name=""),
    path("home/", views.home, name="home"),
    path("index/", views.home, name="home"),
    path("about/", views.AboutView.as_view()),
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    # * User Profile
    path("profile/<str:username>/", views.ProfileView.as_view(), name="profile"),
    # * Item-related URLs
    path("item/<str:item_slug>/", views.item, name="item"),
    path("create_item/", views.create_item, name="create_item"),
    path("search/", views.search, name="search"),
    path("add_review/<int:product_id>/", views.add_review, name="add_review"),
    path(
        "product_detail/<int:product_id>/", views.product_detail, name="product_detail"
    ),
    path("modify_item/<int:item_id>/", views.modify_item, name="modify_item"),
    path("user_items/", views.user_items, name="user_items"),
    path("rating/<str:item_id>/<str:is_like>/", views.rating, name="rating"),
    path("profile/<str:username>/change_data/", views.change_data, name="change_data"),
    path("delete_review/<int:product_id>/", views.delete_review, name="delete_review"),
    # ! CHAT WITH TOKEN
    path("chat/", views.chat, name="chat"),
    path("chat/<slug:room_slug>/<str:token>/", views.room, name="room"),
    path("create_chat_room/", views.create_chat_room, name="create_chat_room"),
    # * MODERATE
    path("moderate/users/", views.ModerateUsersView.as_view(), name="moderate_users"),
    path(
        "moderate/ban/<int:user_id>/",
        views.BanUsersView.as_view(),
        name="moderate_ban_users",
    ),
    path(
        "moderate/unban/<int:user_id>/",
        views.UnbanUsersView.as_view(),
        name="moderate_unban_users",
    ),
    path(
        "moderate/delete/<int:user_id>/",
        views.DeleteUsersView.as_view(),
        name="moderate_delete_users",
    ),
    # * Cart Urls
    path("cart/", views.cart_detail, name="cart_detail"),
    path("add_to_cart/<int:item_id>/", views.add_to_cart, name="add_to_cart"),
    path(
        "remove_from_cart/<int:item_id>/",
        views.remove_from_cart,
        name="remove_from_cart",
    ),
    path(
        "update_cart_quantity/<int:item_id>/",
        views.update_cart_quantity,
        name="update_cart_quantity",
    ),
    path("checkout/", views.checkout, name="checkout"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

websocket_urlpatterns = [
    path("ws/chat/<slug:room_name>/", views_a.ChatConsumer.as_asgi())
]
