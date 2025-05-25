from django.shortcuts import render, redirect
from django.db import connection
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.contrib import messages
from django.http import JsonResponse


@login_required
def create_post(request):
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        image_url = request.POST.get('image_url', '').strip() or None
        
        if not content:
            messages.error(request, "Post content cannot be empty")
            return render(request, "posts/create_post.html", {
                'content': content,
                'image_url': image_url
            })
            
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO Posts (user_id, content, image_url, created_at)
                    VALUES (%s, %s, %s, NOW())
                    RETURNING post_id
                """, [request.user.user_id, content, image_url])
                
                post_id = cursor.fetchone()[0]
                messages.success(request, "Post created successfully!")
                return redirect('post_detail', post_id=post_id)
                
        except Exception as e:
            messages.error(request, "Failed to create post. Please try again.")
            # Log the actual error for debugging
            print(f"Error creating post: {str(e)}")
    
    return render(request, "posts/create_post.html")

@login_required
def post_detail(request, post_id):
    try:
        with connection.cursor() as cursor:
            # Get post with author info
            cursor.execute("""
                SELECT P.*, U.username, U.full_name, U.picture_url,
                       (SELECT COUNT(*) FROM Likes WHERE post_id = P.post_id) as like_count,
                       (SELECT COUNT(*) FROM Comments WHERE post_id = P.post_id) as comment_count
                FROM Posts P
                JOIN Users U ON P.user_id = U.user_id
                WHERE P.post_id = %s
            """,
                [post_id],
            )

            post = dict(
                zip(
                    [col[0] for col in cursor.description], cursor.fetchone() or (None,)
                )
            )

            if not post:
                raise Http404("Post not found")

            # Check if current user liked the post
            cursor.execute(
                """
                SELECT 1 FROM Likes 
                WHERE user_id = %s AND post_id = %s
                LIMIT 1
            """,
                [request.user.user_id, post_id],
            )
            post["is_liked"] = bool(cursor.fetchone())

            # Get comments with author info
            cursor.execute(
                """
                SELECT C.*, U.username, U.full_name, U.picture_url
                FROM Comments C
                JOIN Users U ON C.user_id = U.user_id
                WHERE C.post_id = %s
                ORDER BY C.created_at ASC
            """,
                [post_id],
            )
            comments = [
                dict(zip([col[0] for col in cursor.description], row))
                for row in cursor.fetchall()
            ]

    except Exception as e:
        messages.error(request, "Error loading post")
        print(f"Error loading post: {str(e)}")
        return redirect("users:home")

    return render(
        request, "posts/post_detail.html", {"post": post, "comments": comments}
    )


from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import connection
from django.http import JsonResponse


@login_required
def add_comment(request, post_id):
    if request.method == "POST":
        content = request.POST.get("content", "").strip()
        parent_comment_id = request.POST.get("parent_comment_id", None)

        if not content:
            messages.error(request, "Comment cannot be empty")
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse(
                    {"success": False, "message": "Comment cannot be empty"}, status=400
                )
            return redirect(request.META.get("HTTP_REFERER", "home"))

        try:
            with connection.cursor() as cursor:
                # Use stored procedure sp_AddComment
                cursor.execute(
                    "EXEC sp_AddComment %s, %s, %s, %s",
                    [request.user.user_id, post_id, content, parent_comment_id],
                )
                messages.success(request, "Comment added successfully!")

                # Get the new comment for AJAX response
                if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                    cursor.execute(
                        """
                        SELECT C.comment_id, C.content, C.created_at,
                               U.username, U.full_name, U.picture_url
                        FROM Comments C
                        JOIN Users U ON C.user_id = U.user_id
                        WHERE C.comment_id = (SELECT MAX(comment_id) FROM Comments WHERE post_id = %s AND user_id = %s)
                    """,
                        [post_id, request.user.user_id],
                    )
                    comment = dict(
                        zip([col[0] for col in cursor.description], cursor.fetchone())
                    )
                    cursor.execute(
                        "SELECT COUNT(*) FROM Comments WHERE post_id = %s", [post_id]
                    )
                    comment_count = cursor.fetchone()[0]
                    return JsonResponse(
                        {
                            "success": True,
                            "comment": {
                                "comment_id": comment["comment_id"],
                                "content": comment["content"],
                                "username": comment["username"],
                                "full_name": comment["full_name"],
                                "picture_url": comment["picture_url"]
                                or "/static/images/default-profile.png",
                                "created_at": comment["created_at"].strftime(
                                    "%Y-%m-%d %H:%M:%S"
                                ),
                            },
                            "comment_count": comment_count,
                        }
                    )

        except Exception as e:
            messages.error(request, f"Error adding comment: {str(e)}")
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse({"success": False, "message": str(e)}, status=400)

        return redirect(request.META.get("HTTP_REFERER", "users:home"))

    return redirect("users:home")


from django.shortcuts import render, get_object_or_404
from django.db import connection
from django.contrib.auth.decorators import login_required


@login_required
def post_detail(request, post_id):
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT 
                    P.post_id, P.content, P.image_url, P.created_at,
                    U.user_id AS author_id, U.username AS author_username,
                    U.full_name AS author_full_name, U.picture_url AS author_picture_url,
                    (SELECT COUNT(*) FROM Likes L WHERE L.post_id = P.post_id) AS like_count,
                    (SELECT COUNT(*) FROM Comments C WHERE C.post_id = P.post_id) AS comment_count,
                    (SELECT 1 FROM Likes L WHERE L.post_id = P.post_id AND L.user_id = %s) AS is_liked
                FROM Posts P
                JOIN Users U ON P.user_id = U.user_id
                WHERE P.post_id = %s
                """,
                [request.user.user_id, post_id],
            )
            columns = [col[0] for col in cursor.description]
            post_data = cursor.fetchone()
            if not post_data:
                return HttpResponse("Post not found", status=404)
            post = dict(zip(columns, post_data))
            print(f"Raw post data: {post_data}")  # Debug
            print(f"Post dict: {post}")  # Debug
            post["is_liked"] = bool(post["is_liked"])
            post["author_username"] = post.get("author_username") or "Unknown"

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
            print(f"Comments: {comments}")  # Debug
            for comment in comments:
                comment["commenter_username"] = (
                    comment.get("commenter_username") or "Unknown"
                )

        return render(
            request, "posts/post_detail.html", {"post": post, "comments": comments}
        )
    except Exception as e:
        messages.error(request, f"Error loading post: {str(e)}")
        return redirect("users:home")


@login_required
def like_post(request, post_id):
    if request.method == "POST":
        try:
            with connection.cursor() as cursor:
                # Use stored procedure sp_LikePost
                cursor.execute(
                    "EXEC sp_LikePost %s, %s", [request.user.user_id, post_id]
                )
                messages.success(request, "Post liked successfully!")
        except Exception as e:
            # Check if the error is due to already liking the post
            if "User has already liked this post" in str(e):
                # Unlike the post by deleting the like
                with connection.cursor() as cursor:
                    cursor.execute(
                        "DELETE FROM Likes WHERE user_id = %s AND post_id = %s",
                        [request.user.user_id, post_id],
                    )
                    messages.success(request, "Post unliked")
            else:
                messages.error(request, f"Error: {str(e)}")

        # Handle AJAX request
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT COUNT(*) FROM Likes WHERE post_id = %s", [post_id]
                )
                like_count = cursor.fetchone()[0]
                cursor.execute(
                    "SELECT 1 FROM Likes WHERE user_id = %s AND post_id = %s",
                    [request.user.user_id, post_id],
                )
                is_liked = bool(cursor.fetchone())
                return JsonResponse(
                    {"success": True, "like_count": like_count, "is_liked": is_liked}
                )

        return redirect(request.META.get("HTTP_REFERER", "users:home"))

    return redirect("users:home")
