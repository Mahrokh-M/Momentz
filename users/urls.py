from django.urls import path
from . import views


urlpatterns = [
    path("", views.home, name="home"),
    path("profile/<str:username>/", views.profile, name="profile"),
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),
    path("follow/<int:user_id>/", views.follow_user, name="follow_user"),
    path("discover/", views.discover_users, name="discover_users"),
    path("create/", views.create_post, name="create_post"),
]

