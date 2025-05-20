from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("users.urls")),
    path("posts/", include("posts.urls")),
    path("messages/", include("messaging.urls")),
    path("notifications/", include("notifications.urls")),
]
