from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from contracts import views

urlpatterns = [
    path("", views.home, name="home"),
    path("api/contracts/", views.contracts, name="contracts"),
    # path("api/contract/<int:id>", views.contract, name="contract"),
    # path("api/contragents/<int:id>", views.contragents, name="contragents"),
    # path("api/contragent/<int:id>", views.contragent, name="contragent"),
    # path("api/users/", views.users, name="users/"),
    # path("api/user/<int:id>", views.user, name="user"),
    # path("api/comments/", views.comments, name="comments"),
    # path("api/comment/<int:id>", views.comment, name="comment"),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
