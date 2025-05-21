from django.shortcuts import render, redirect, get_object_or_404
from django.db import connection
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from .models import Post, Like, Comment

@login_required
def create_post(request):
    if request.method == 'POST':
        content = request.POST.get('content')
        image_url = request.POST.get('image_url', None)
        
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO Posts (user_id, content, image_url)
                    VALUES (%s, %s, %s)
                """, [request.user.user_id, content, image_url])
                
                messages.success(request, "Post created successfully!")
                return redirect('home')
        except Exception as e:
            messages.error(request, f"Error creating post: {str(e)}")
    
    return render(request, "posts/create_post.html")

@login_required
def post_detail(request, post_id):
    # Get post details
    with connection.cursor() as cursor:
        # Get post
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
        post_data = cursor.fetchone()
        
        if not post_data:
            return HttpResponse("Post not found", status=404)
            
        post = dict(zip(columns, post_data))
        
        # Check if current user liked the post
        cursor.execute("""
            SELECT COUNT(*) FROM Likes 
            WHERE user_id = %s AND post_id = %s
        """, [request.user.user_id, post_id])
        is_liked = cursor.fetchone()[0] > 0
        
        # Get comments
        cursor.execute("""
            SELECT C.comment_id, C.content, C.created_at,
                   U.user_id, U.username, U.full_name, U.picture_url
            FROM Comments C
            JOIN Users U ON C.user_id = U.user_id
            WHERE C.post_id = %s
            ORDER BY C.created_at DESC
        """, [post_id])
        columns = [col[0] for col in cursor.description]
        comments = [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    return render(request, "posts/post_detail.html", {
        "post": post,
        "is_liked": is_liked,
        "comments": comments
    })

@login_required
def like_post(request, post_id):
    if request.method == 'POST':
        try:
            with connection.cursor() as cursor:
                cursor.execute("EXEC sp_LikePost %s, %s", [request.user.user_id, post_id])
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
        
        return redirect(request.META.get('HTTP_REFERER', 'home'))
    
    return redirect('home')

@login_required
def add_comment(request, post_id):
    if request.method == 'POST':
        content = request.POST.get('content')
        parent_comment_id = request.POST.get('parent_comment_id', None)
        
        try:
            with connection.cursor() as cursor:
                cursor.execute("EXEC sp_AddComment %s, %s, %s, %s", 
                             [request.user.user_id, post_id, content, parent_comment_id])
                
                messages.success(request, "Comment added successfully!")
        except Exception as e:
            messages.error(request, f"Error adding comment: {str(e)}")
        
        return redirect(request.META.get('HTTP_REFERER', 'home'))
    
    return redirect('home')