from django.contrib import admin
from django.urls import path, include
from django.conf import settings

urlpatterns = [

    path('admin/', admin.site.urls),
    path('', include('users.urls', namespace='users')),
    path('posts/', include('posts.urls', namespace='posts')),
    path('messaging/', include('messaging.urls', namespace='messaging')),
    path('notifications/', include('notifications.urls', namespace='notifications')),
]
