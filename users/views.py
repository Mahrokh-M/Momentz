from django.shortcuts import render, redirect
from django.db import connection
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from .models import User


@login_required
def home(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("EXEC GetUserFeed %s", [request.user.user_id])
            columns = [col[0] for col in cursor.description]
            posts = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            # Check if user follows anyone
            cursor.execute("SELECT COUNT(*) FROM Followers WHERE follower_user_id = %s", [request.user.user_id])
            following_count = cursor.fetchone()[0]
            
        if not posts and following_count == 0:
            messages.info(request, "You're not following anyone yet. Discover users to see their posts!")
            
        return render(request, "home.html", {
            "posts": posts,
            "following_count": following_count
        })
    except Exception as e:
        messages.error(request, f"Error loading feed: {str(e)}")
        return render(request, "home.html", {"posts": []})

@login_required
def profile(request, username):
    try:
        with connection.cursor() as cursor:
            # Get profile data
            cursor.execute("SELECT * FROM UserProfileView WHERE username = %s", [username])
            columns = [col[0] for col in cursor.description]
            profile_data = cursor.fetchone()
            
            if not profile_data:
                return HttpResponse("User not found", status=404)
                
            profile = dict(zip(columns, profile_data))
            
            # Check if current user follows this profile
            cursor.execute("SELECT dbo.IsFollowing(%s, %s) AS is_following", 
                         [request.user.user_id, profile['user_id']])
            is_following = cursor.fetchone()[0]
            
            # Query posts for the user
            cursor.execute("""
                SELECT P.post_id, P.content, P.image_url, P.created_at,
                       (SELECT COUNT(*) FROM Likes L WHERE L.post_id = P.post_id) AS like_count,
                       (SELECT COUNT(*) FROM Comments C WHERE C.post_id = P.post_id) AS comment_count
                FROM Posts P
                WHERE P.user_id = %s
                ORDER BY P.created_at DESC
            """, [profile['user_id']])
            columns = [col[0] for col in cursor.description]
            posts = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
        return render(request, "profile.html", {
            "profile": profile,
            "posts": posts,
            "is_following": is_following
        })
    except Exception as e:
        messages.error(request, f"Error loading profile: {str(e)}")
        return redirect('home')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')  # Only username, no email
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)  # Check username only
            if user.check_password(password):
                auth_login(request, user, backend='users.auth.SQLServerAuthBackend')
                return redirect('home')
            else:
                messages.error(request, "Invalid password")
        except User.DoesNotExist:
            messages.error(request, "Username not found")

    return render(request, "login.html")


from django.db import connection
from django.contrib.auth.hashers import make_password

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        full_name = request.POST.get('full_name', '')

        try:
            with connection.cursor() as cursor:
                # Check if user exists
                cursor.execute("SELECT 1 FROM Users WHERE username = %s OR email = %s", [username, email])
                if cursor.fetchone():
                    messages.error(request, "Username or email already exists")
                    return render(request, "register.html", {
                        'username': username,
                        'email': email,
                        'full_name': full_name
                    })
                
                # Insert new user (without last_login)
                hashed_pw = make_password(password)
                cursor.execute(
                    "INSERT INTO Users (username, email, password_hash, full_name, created_at) "
                    "VALUES (%s, %s, %s, %s, GETDATE())",
                    [username, email, hashed_pw, full_name]
                )
                
                # Get the new user
                cursor.execute(
                    "SELECT user_id, username, email, password_hash, full_name, created_at "
                    "FROM Users WHERE username = %s", 
                    [username]
                )
                row = cursor.fetchone()
                user = User(
                    user_id=row[0],
                    username=row[1],
                    email=row[2],
                    password_hash=row[3],
                    full_name=row[4],
                    created_at=row[5]
                )
                
                auth_login(request, user, backend='users.auth.SQLServerAuthBackend')
                return redirect('home')
                
        except Exception as e:
            messages.error(request, f"Registration failed: {str(e)}")
    
    return render(request, "register.html")

@login_required
def logout_view(request):
    auth_logout(request)
    return redirect('login')


@login_required
def follow_user(request, user_id):
    if request.method == 'POST':
        try:
            username = request.POST.get('username')
            with connection.cursor() as cursor:
                # Check follow status
                cursor.execute("SELECT dbo.IsFollowing(%s, %s) AS is_following", 
                              [request.user.user_id, user_id])
                is_following = cursor.fetchone()[0]
                
                if is_following:
                    # Unfollow
                    cursor.execute("DELETE FROM Followers WHERE follower_user_id = %s AND following_user_id = %s",
                                 [request.user.user_id, user_id])
                    messages.success(request, f"You unfollowed {username}")
                else:
                    # Follow
                    cursor.execute("EXEC sp_FollowUser %s, %s", [request.user.user_id, user_id])
                    messages.success(request, f"You are now following {username}")
                
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
        
        # Redirect back to where the request came from
        return redirect(request.META.get('HTTP_REFERER', 'home'))
    
    return redirect('home')

@login_required
def discover_users(request):
    try:
        with connection.cursor() as cursor:
            # Get all users except current user and those already followed
            cursor.execute("""
                SELECT U.user_id, U.username, U.full_name, U.picture_url,
                       dbo.IsFollowing(%s, U.user_id) AS is_following
                FROM Users U
                WHERE U.user_id != %s
                ORDER BY U.username
            """, [request.user.user_id, request.user.user_id])
            
            columns = [col[0] for col in cursor.description]
            users = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
        return render(request, "discover.html", {"users": users})
    except Exception as e:
        messages.error(request, f"Error loading users: {str(e)}")
        return redirect('home')