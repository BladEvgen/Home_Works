from clothes_app import views
from django.urls import path
from clothes_app.swagger import urlpatterns as doc_urls
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", views.home),
    path("api/messages/", views.warning_messages),
    path("api/get_person_info", views.get_person_data_by_id),
    path("api/delete_clothes", views.delete_clothes),
    path("api/add_clothe", views.insert_new_clothe),
    path("api/update_clothe", views.update_clothe),
    path("api/worn_cloth_info", views.get_worn_clothes),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += doc_urls
