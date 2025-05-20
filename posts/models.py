from django.db import models
from users.models import User


class Post(models.Model):
    post_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column="user_id")
    content = models.TextField()
    image_url = models.CharField(max_length=255, null=True)
    created_at = models.DateTimeField()

    class Meta:
        db_table = "Posts"
        managed = False


class PostEngagement(models.Model):
    post_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, db_column="author_id")
    content = models.TextField()
    created_at = models.DateTimeField()

    class Meta:
        db_table = "PostEngagementView"
        managed = False


class Like(models.Model):
    like_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column="user_id")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, db_column="post_id")
    created_at = models.DateTimeField()

    class Meta:
        db_table = "Likes"
        managed = False


class Comment(models.Model):
    comment_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column="user_id")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, db_column="post_id")
    content = models.TextField()
    parent_comment = models.ForeignKey(
        "self", null=True, on_delete=models.CASCADE, db_column="parent_comment_id"
    )
    created_at = models.DateTimeField()

    class Meta:
        db_table = "Comments"
        managed = False
