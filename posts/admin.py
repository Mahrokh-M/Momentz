from django.contrib import admin
from django.db import connection
from django import forms
from .models import Post, Like, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["user", "content", "image_url"]

from django.contrib import admin
from django.db import connection
from django import forms
from .models import Post, Like, Comment

class PostAdmin(admin.ModelAdmin):
    list_display = ("post_id", "user", "content", "created_at")
    search_fields = ("content",)
    list_filter = ("created_at",)

    def save_model(self, request, obj, form, change):
        with connection.cursor() as cursor:
            if change:
                cursor.execute(
                    "UPDATE Posts SET user_id = %s, content = %s, image_url = %s WHERE post_id = %s",
                    [obj.user.user_id, obj.content, obj.image_url, obj.post_id]
                )
            else:
                cursor.execute(
                    "INSERT INTO Posts (user_id, content, image_url, created_at) VALUES (%s, %s, %s, NOW())",
                    [obj.user.user_id, obj.content, obj.image_url]
                )

    def delete_model(self, request, obj):
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM Posts WHERE post_id = %s", [obj.post_id])


class LikeForm(forms.ModelForm):
    class Meta:
        model = Like
        fields = ["user", "post"]


class LikeAdmin(admin.ModelAdmin):
    list_display = ("like_id", "user", "post", "created_at")
    list_filter = ("created_at",)
    form = LikeForm

    def save_model(self, request, obj, form, change):
        with connection.cursor() as cursor:
            cursor.execute("EXEC sp_LikePost %s, %s", [obj.user_id, obj.post_id])

    def delete_model(self, request, obj):
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM Likes WHERE like_id = %s", [obj.like_id])


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["user", "post", "content", "parent_comment"]


class CommentAdmin(admin.ModelAdmin):
    list_display = ("comment_id", "user", "post", "content", "created_at")
    search_fields = ("content",)
    list_filter = ("created_at",)
    form = CommentForm

    def save_model(self, request, obj, form, change):
        with connection.cursor() as cursor:
            cursor.execute(
                "EXEC sp_AddComment %s, %s, %s, %s",
                [
                    form.cleaned_data["user"].user_id,
                    form.cleaned_data["post"].post_id,
                    form.cleaned_data["content"],
                    (
                        form.cleaned_data["parent_comment"].comment_id
                        if form.cleaned_data["parent_comment"]
                        else None
                    ),
                ],
            )

    def delete_model(self, request, obj):
        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM Comments WHERE comment_id = %s", [obj.comment_id]
            )




admin.site.register(Post, PostAdmin)
admin.site.register(Like)
admin.site.register(Comment)
