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
        user_id = request.user.user_id
        # Fetch posts from users the current user follows
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT 
                    P.post_id, P.content, P.image_url, P.created_at,
                    U.user_id AS author_id, U.username AS author_username,
                    U.full_name AS author_full_name, U.picture_url AS author_picture_url,
                    (SELECT COUNT(*) FROM Likes L WHERE L.post_id = P.post_id) AS like_count,
                    (SELECT COUNT(*) FROM Comments C WHERE C.post_id = P.post_id) AS comment_count
                FROM Posts P
                JOIN Users U ON P.user_id = U.user_id
                JOIN Followers F ON F.followed_id = U.user_id
                WHERE F.follower_id = %s
                ORDER BY P.created_at DESC
            """,
                [user_id],
            )
            columns = [col[0] for col in cursor.description]
            posts = [dict(zip(columns, row)) for row in cursor.fetchall()]

        # Count the number of users the current user is following
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(*) FROM Followers WHERE follower_id = %s", [user_id]
            )
            following_count = cursor.fetchone()[0]

        # Debug information
        post_dict = {post["post_id"]: post for post in posts}

        # Debug logging
        print(f"User ID: {user_id}")
        print(f"Posts: {posts}")
        print(f"Following Count: {following_count}")
        print(f"Post Dict: {post_dict}")

        return render(
            request,
            "users/home.html",
            {
                "posts": posts,
                "following_count": following_count,
                "debug": True,  # Enable debug for now
                "post_dict": post_dict if posts else None,
            },
        )
    except Exception as e:
        messages.error(request, f"Error loading feed: {str(e)}")
        print(f"Error in home view: {str(e)}")  # Log the error for debugging
        return render(
            request,
            "users/home.html",
            {"posts": [], "following_count": 0, "debug": True, "post_dict": None},
        )


@login_required
def profile(request, username):
    try:
        with connection.cursor() as cursor:
            # Get profile data
            cursor.execute(
                "SELECT * FROM UserProfileView WHERE username = %s", [username]
            )
            columns = [col[0] for col in cursor.description]
            profile_data = cursor.fetchone()

            if not profile_data:
                return HttpResponse("User not found", status=404)

            profile = dict(zip(columns, profile_data))

            # Check if current user follows this profile
            cursor.execute(
                "SELECT dbo.IsFollowing(%s, %s) AS is_following",
                [request.user.user_id, profile["user_id"]],
            )
            is_following = cursor.fetchone()[0]

            # Query posts for the user
            cursor.execute(
                """
                SELECT P.post_id, P.content, P.image_url, P.created_at,
                       (SELECT COUNT(*) FROM Likes L WHERE L.post_id = P.post_id) AS like_count,
                       (SELECT COUNT(*) FROM Comments C WHERE C.post_id = P.post_id) AS comment_count
                FROM Posts P
                WHERE P.user_id = %s
                ORDER BY P.created_at DESC
            """,
                [profile["user_id"]],
            )
            columns = [col[0] for col in cursor.description]
            posts = [dict(zip(columns, row)) for row in cursor.fetchall()]

        return render(
            request,
            "users/profile.html",
            {"profile": profile, "posts": posts, "is_following": is_following},
        )
    except Exception as e:
        messages.error(request, f"Error loading profile: {str(e)}")
        return redirect("home")


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")  # Only username, no email
        password = request.POST.get("password")

        try:
            user = User.objects.get(username=username)  # Check username only
            if user.check_password(password):
                auth_login(request, user, backend="users.auth.SQLServerAuthBackend")
                return redirect("home")
            else:
                messages.error(request, "Invalid password")
        except User.DoesNotExist:
            messages.error(request, "Username not found")

    return render(request, "users/login.html")


def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        full_name = request.POST.get("full_name", "")

        try:
            with connection.cursor() as cursor:
                # Check if user exists
                cursor.execute(
                    "SELECT 1 FROM Users WHERE username = %s OR email = %s",
                    [username, email],
                )
                if cursor.fetchone():
                    messages.error(request, "Username or email already exists")
                    return render(
                        request,
                        "users/register.html",
                        {"username": username, "email": email, "full_name": full_name},
                    )

                # Insert new user (without last_login)
                hashed_pw = make_password(password)
                cursor.execute(
                    "INSERT INTO Users (username, email, password_hash, full_name, created_at) "
                    "VALUES (%s, %s, %s, %s, GETDATE())",
                    [username, email, hashed_pw, full_name],
                )

                # Get the new user
                cursor.execute(
                    "SELECT user_id, username, email, password_hash, full_name, created_at "
                    "FROM Users WHERE username = %s",
                    [username],
                )
                row = cursor.fetchone()
                user = User(
                    user_id=row[0],
                    username=row[1],
                    email=row[2],
                    password_hash=row[3],
                    full_name=row[4],
                    created_at=row[5],
                )

                auth_login(request, user, backend="users.auth.SQLServerAuthBackend")
                return redirect("home")

        except Exception as e:
            messages.error(request, f"Registration failed: {str(e)}")

    return render(request, "users/register.html")


@login_required
def logout_view(request):
    auth_logout(request)
    return redirect("login")


@login_required
def follow_user(request, user_id):
    if request.method == "POST":
        try:
            with connection.cursor() as cursor:
                # Check if already following using your IsFollowing function
                cursor.execute(
                    "SELECT dbo.IsFollowing(%s, %s) AS is_following",
                    [request.user.user_id, user_id],
                )
                is_following = cursor.fetchone()[0]

                if is_following:
                    # UNFOLLOW LOGIC
                    cursor.execute(
                        """
                        DELETE FROM Followers 
                        WHERE follower_id = %s AND followed_id = %s
                    """,
                        [request.user.user_id, user_id],
                    )
                    messages.success(request, "Successfully unfollowed user")
                else:
                    # FOLLOW LOGIC (using your existing sp_FollowUser)
                    cursor.execute(
                        "EXEC sp_FollowUser %s, %s", [request.user.user_id, user_id]
                    )
                    messages.success(request, "Successfully followed user")

                # Update the follow status immediately for the template
                cursor.execute(
                    "SELECT dbo.IsFollowing(%s, %s) AS is_following",
                    [request.user.user_id, user_id],
                )
                is_following = cursor.fetchone()[0]

        except Exception as e:
            messages.error(request, f"Error: {str(e)}")

        return redirect(request.META.get("HTTP_REFERER", "home"))

    return redirect("home")


@login_required
def discover_users(request):
    try:
        with connection.cursor() as cursor:
            # Get all users except current user and those already followed
            cursor.execute(
                """
                SELECT U.user_id, U.username, U.full_name, U.picture_url,
                       dbo.IsFollowing(%s, U.user_id) AS is_following
                FROM Users U
                WHERE U.user_id != %s
                ORDER BY U.username
            """,
                [request.user.user_id, request.user.user_id],
            )

            columns = [col[0] for col in cursor.description]
            users = [dict(zip(columns, row)) for row in cursor.fetchall()]

        return render(request, "users/discover.html", {"users": users})
    except Exception as e:
        messages.error(request, f"Error loading users: {str(e)}")
        return redirect("home")


@login_required
def create_post(request):
    if request.method == "POST":
        content = request.POST.get("content")
        image_url = request.POST.get("image_url", None)

        if not content:
            messages.error(request, "Content is required")
            return render(request, "users/create_post.html")

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO Posts (user_id, content, image_url, created_at) "
                    "VALUES (%s, %s, %s, GETDATE())",
                    [request.user.user_id, content, image_url],
                )
                messages.success(request, "Post created successfully!")
                return redirect("home")
        except Exception as e:
            messages.error(request, f"Error creating post: {str(e)}")
            return render(
                request,
                "users/create_post.html",
                {"content": content, "image_url": image_url},
            )

    return render(request, "users/create_post.html")


@login_required
def post_detail(request, post_id):
    try:
        with connection.cursor() as cursor:
            # Fetch post details
            cursor.execute(
                """
                SELECT 
                    P.post_id, P.content, P.image_url, P.created_at,
                    U.user_id AS author_id, U.username AS author_username,
                    U.full_name AS author_full_name, U.picture_url AS author_picture_url,
                    (SELECT COUNT(*) FROM Likes L WHERE L.post_id = P.post_id) AS like_count,
                    (SELECT COUNT(*) FROM Comments C WHERE C.post_id = P.post_id) AS comment_count
                FROM Posts P
                JOIN Users U ON P.user_id = U.user_id
                WHERE P.post_id = %s
            """,
                [post_id],
            )
            columns = [col[0] for col in cursor.description]
            post_data = cursor.fetchone()

            if not post_data:
                return HttpResponse("Post not found", status=404)

            post = dict(zip(columns, post_data))

            # Fetch comments
            cursor.execute(
                """
                SELECT 
                    C.comment_id, C.content, C.created_at,
                    U.user_id AS commenter_id, U.username AS commenter_username,
                    U.full_name AS commenter_full_name, U.picture_url AS commenter_picture_url
                FROM Comments C
                JOIN Users U ON C.user_id = U.user_id
                WHERE C.post_id = %s
                ORDER BY C.created_at ASC
            """,
                [post_id],
            )
            columns = [col[0] for col in cursor.description]
            comments = [dict(zip(columns, row)) for row in cursor.fetchall()]

        return render(
            request, "users/post_detail.html", {"post": post, "comments": comments}
        )
    except Exception as e:
        messages.error(request, f"Error loading post: {str(e)}")
        return redirect("home")
