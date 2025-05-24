from django.shortcuts import render, redirect
from django.db import connection
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.contrib import messages

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
            """, [post_id])
            
            post = dict(zip(
                [col[0] for col in cursor.description],
                cursor.fetchone() or (None,)
            ))
            
            if not post:
                raise Http404("Post not found")
                
            # Check if current user liked the post
            cursor.execute("""
                SELECT 1 FROM Likes 
                WHERE user_id = %s AND post_id = %s
                LIMIT 1
            """, [request.user.user_id, post_id])
            post['is_liked'] = bool(cursor.fetchone())
            
            # Get comments with author info
            cursor.execute("""
                SELECT C.*, U.username, U.full_name, U.picture_url
                FROM Comments C
                JOIN Users U ON C.user_id = U.user_id
                WHERE C.post_id = %s
                ORDER BY C.created_at ASC
            """, [post_id])
            comments = [
                dict(zip([col[0] for col in cursor.description], row))
                for row in cursor.fetchall()
            ]
            
    except Exception as e:
        messages.error(request, "Error loading post")
        print(f"Error loading post: {str(e)}")
        return redirect('home')
    
    return render(request, "posts/post_detail.html", {
        'post': post,
        'comments': comments
    })



@login_required
def like_post(request, post_id):
    if request.method == 'POST':
        try:
            with connection.cursor() as cursor:
                # Check if already liked
                cursor.execute(
                    "SELECT 1 FROM Likes WHERE user_id = %s AND post_id = %s",
                    [request.user.user_id, post_id]
                )
                if cursor.fetchone():
                    cursor.execute(
                        "DELETE FROM Likes WHERE user_id = %s AND post_id = %s",
                        [request.user.user_id, post_id]
                    )
                    messages.success(request, "Post unliked")
                else:
                    cursor.execute(
                        "INSERT INTO Likes (user_id, post_id, created_at) VALUES (%s, %s, NOW())",
                        [request.user.user_id, post_id]
                    )
                    messages.success(request, "Post liked")
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
    
    return redirect(request.META.get('HTTP_REFERER', 'home'))

@login_required
def add_comment(request, post_id):
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        parent_comment_id = request.POST.get('parent_comment_id', None)
        
        if not content:
            messages.error(request, "Comment cannot be empty")
            return redirect(request.META.get('HTTP_REFERER', 'home'))
            
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO Comments (user_id, post_id, content, parent_comment_id, created_at) "
                    "VALUES (%s, %s, %s, %s, NOW())",
                    [request.user.user_id, post_id, content, parent_comment_id]
                )
                messages.success(request, "Comment added successfully!")
        except Exception as e:
            messages.error(request, f"Error adding comment: {str(e)}")
    
    return redirect(request.META.get('HTTP_REFERER', 'home'))



from django.shortcuts import render, get_object_or_404
from django.db import connection
from django.contrib.auth.decorators import login_required

@login_required
def post_detail(request, post_id):
    try:
        with connection.cursor() as cursor:
            # Get post details
            cursor.execute("""
                SELECT P.post_id, P.content, P.image_url, P.created_at,
                       U.user_id, U.username, U.full_name, U.picture_url,
                       (SELECT COUNT(*) FROM Likes L WHERE L.post_id = P.post_id) AS like_count,
                       (SELECT COUNT(*) FROM Comments C WHERE C.post_id = P.post_id) AS comment_count
                FROM Posts P
                JOIN Users U ON P.user_id = U.user_id
                WHERE P.post_id = %s
            """, [post_id])
            
            columns = [col[0] for col in cursor.description]
            post = dict(zip(columns, cursor.fetchone()))
            
            # Get comments
            cursor.execute("""
                SELECT C.comment_id, C.content, C.created_at,
                       U.user_id, U.username, U.full_name, U.picture_url
                FROM Comments C
                JOIN Users U ON C.user_id = U.user_id
                WHERE C.post_id = %s
                ORDER BY C.created_at DESC
            """, [post_id])
            
            comments = [dict(zip([col[0] for col in cursor.description], row)) 
                      for row in cursor.fetchall()]
            
        return render(request, "posts/post_detail.html", {
            "post": post,
            "comments": comments
        })
        
    except Exception as e:
        return render(request, "error.html", {"message": str(e)})