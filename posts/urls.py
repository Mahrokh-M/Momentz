from django.urls import path
from . import views

urlpatterns = [
    path("create/", views.create_post, name="create_post"),
    path("<int:post_id>/", views.post_detail, name="post_detail"),
    path("like/<int:post_id>/", views.like_post, name="like_post"),
    path("comment/<int:post_id>/", views.add_comment, name="add_comment"),
]