from django.urls import path
from . import views

urlpatterns = [
    path("", views.inbox, name="inbox"),
    path("chat/<str:username>/", views.chat, name="chat"),
    path("send/", views.send_message, name="send_message"),
    path(
        "mark_read/<int:message_id>/", views.mark_message_read, name="mark_message_read"
    ),
]
