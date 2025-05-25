from django.db import models
from users.models import User


class Message(models.Model):
    message_id = models.AutoField(primary_key=True)
    sender = models.ForeignKey(
        User,
        related_name="sent_messages",
        on_delete=models.CASCADE,
        db_column="sender_id",
    )
    receiver = models.ForeignKey(
        User,
        related_name="received_messages",
        on_delete=models.CASCADE,
        db_column="receiver_id",
    )
    content = models.TextField()
    sent_at = models.DateTimeField()
    is_read = models.BooleanField(default=False)

    class Meta:
        db_table = "Messages"
        managed = False

    # Either remove the __str__ method completely or change it to something simpler:
    def __str__(self):
        return f"Message #{self.message_id}"  # Or just return self.content
