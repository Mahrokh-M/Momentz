from django.http import HttpResponse
from django.db import connection


def create_post(request):
    # Placeholder: Call sp_CreatePost stored procedure
    return HttpResponse("Create post (not implemented yet)")


def like_post(request, post_id):
    # Placeholder: Call sp_LikePost stored procedure
    return HttpResponse(f"Like post {post_id} (not implemented yet)")


def add_comment(request, post_id):
    # Placeholder: Call sp_AddComment stored procedure
    return HttpResponse(f"Add comment to post {post_id} (not implemented yet)")
