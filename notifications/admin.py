from django.contrib import admin
from django.db import connection
from django import forms
from .models import Notification


class NotificationForm(forms.ModelForm):
    class Meta:
        model = Notification
        fields = [
            "user",
            "related_user",
            "related_post",
            "notification_type",
            "content",
        ]


class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        "notification_id",
        "user",
        "related_user",
        "notification_type",
        "content",
        "created_at",
        "is_read",
    )
    search_fields = ("content",)
    list_filter = ("notification_type", "is_read", "created_at")
    form = NotificationForm

    def get_queryset(self, request):
        return super().get_queryset(request)

    def save_model(self, request, obj, form, change):
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO Notifications (user_id, related_user_id, related_post_id, notification_type, content) VALUES (%s, %s, %s, %s, %s)",
                [
                    form.cleaned_data["user"].user_id,
                    form.cleaned_data["related_user"].user_id,
                    (
                        form.cleaned_data["related_post"].post_id
                        if form.cleaned_data["related_post"]
                        else None
                    ),
                    form.cleaned_data["notification_type"],
                    form.cleaned_data["content"],
                ],
            )

    def delete_model(self, request, obj):
        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM Notifications WHERE notification_id = %s",
                [obj.notification_id],
            )


admin.site.register(Notification, NotificationAdmin)
