from django.db import models
from users.models import User
from posts.models import Post


class Notification(models.Model):
    notification_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column="user_id")
    related_user = models.ForeignKey(
        User,
        related_name="related_notifications",
        on_delete=models.CASCADE,
        db_column="related_user_id",
    )
    related_post = models.ForeignKey(
        Post, null=True, on_delete=models.CASCADE, db_column="related_post_id"
    )
    notification_type = models.CharField(max_length=20)
    content = models.CharField(max_length=255)
    created_at = models.DateTimeField()
    is_read = models.BooleanField(default=False)

    class Meta:
        db_table = "Notifications"
        managed = False
