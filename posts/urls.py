from django.urls import path
from . import views

app_name = 'posts'

urlpatterns = [
    path('create/', views.create_post, name='create_post'),
    path('<int:post_id>/', views.post_detail, name='post_detail'),
    path('<int:post_id>/like/', views.like_post, name='like'),
    path('<int:post_id>/comment/', views.add_comment, name='comment'),
]