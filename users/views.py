from django.shortcuts import render, redirect
from django.db import connection
from django.contrib.auth import login, logout
from django.http import HttpResponse


def home(request):
    # Query UserFeedView for the logged-in user's feed
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM UserFeedView WHERE user_id = %s", [1])
        posts = cursor.fetchall()
    return render(request, "home.html", {"posts": posts})


def profile(request, username):
    # Query UserProfileView for the user's profile
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM UserProfileView WHERE username = %s", [username])
        profile = cursor.fetchone()
        if not profile:
            return HttpResponse("User not found", status=404)
        # Query posts for the user (assuming UserFeedView or similar)
        cursor.execute("SELECT * FROM UserFeedView WHERE username = %s", [username])
        posts = cursor.fetchall()
    return render(request, "profile.html", {"profile": profile, "posts": posts})


def login_view(request):
    # Placeholder for login (to be implemented)
    return HttpResponse("Login page (not implemented yet)")


def register_view(request):
    # Placeholder for registration (to be implemented)
    return HttpResponse("Register page (not implemented yet)")


def logout_view(request):
    # Placeholder for logout (to be implemented)
    return HttpResponse("Logout page (not implemented yet)")
