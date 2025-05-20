from django.db import models


class User(models.Model):
    user_id = models.AutoField(primary_key=True, db_column="user_id")
    username = models.CharField(max_length=50, unique=True)
    email = models.CharField(max_length=100, unique=True)
    password_hash = models.CharField(max_length=255)
    full_name = models.CharField(max_length=100, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    picture_url = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "Users"
        managed = False


class Follower(models.Model):
    follower_id = models.AutoField(primary_key=True)
    follower_user = models.ForeignKey(
        User,
        related_name="following",
        on_delete=models.CASCADE,
        db_column="follower_user_id",
    )
    following_user = models.ForeignKey(
        User,
        related_name="followers",
        on_delete=models.CASCADE,
        db_column="following_user_id",
    )
    created_at = models.DateTimeField()

    class Meta:
        db_table = "Followers"
        managed = False
