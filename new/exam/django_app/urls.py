from django.urls import path
from django_app import views
from rest_framework_simplejwt.views import (
    TokenVerifyView,
    TokenRefreshView,
    TokenObtainPairView,
)

urlpatterns = [
    path("", views.home, name="home"),
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("about/", views.AboutView.as_view(), name="about"),
    path("profile/<str:username>/", views.ProfileView.as_view(), name="profile"),
    path("profile/<str:username>/change_data/", views.change_data, name="change_data"),
    path("post_detail/<int:post_id>", views.post_detail, name="post_detail"),
    path("raiting/<str:post_id>/<str:is_like>/", views.raiting, name="raiting"),
    path("user_posts/", views.user_posts, name="user_posts"),
    path("add_comment/<int:post_id>/", views.add_comment, name="add_comment"),
    path("delete_review/<int:post_id>/", views.delete_review, name="delete_review"),
    path("create_post/", views.create_post, name="create_post"),
    path("modify_post/<int:post_id>/", views.modify_post, name="modify_post"),
    # * Users API
    path("api/users/", views.UserListCreateAPIView.as_view(), name="user-list-create"),
    path(
        "api/users/<int:pk>/",
        views.UserRetrieveUpdateDestroyAPIView.as_view(),
        name="user-detail",
    ),
    #! Tokens
    path("api/token/", TokenObtainPairView.as_view()),
    path("api/token/refresh/", TokenRefreshView.as_view()),
    path("api/token/verify/", TokenVerifyView.as_view()),
]
