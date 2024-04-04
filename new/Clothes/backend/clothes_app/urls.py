from clothes_app import views
from django.urls import path

urlpatterns = [
    path("", views.home),
    path("api/messages/", views.warning_messages),
]
