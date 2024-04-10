from clothes_app import views
from django.urls import path
from clothes_app.swagger import urlpatterns as doc_urls
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", views.home),
    path("api/messages/", views.warning_messages),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += doc_urls
