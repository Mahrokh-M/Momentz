from django.contrib import admin
from django.db import connection
from django import forms
from .models import Message


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ["sender", "receiver", "content"]


class MessageAdmin(admin.ModelAdmin):
    list_display = ("message_id", "sender", "receiver", "content", "sent_at", "is_read")
    search_fields = ("content",)
    list_filter = ("sent_at", "is_read")
    form = MessageForm

    def get_queryset(self, request):
        # Return a proper QuerySet that matches your model
        return Message.objects.all()

    def save_model(self, request, obj, form, change):
        with connection.cursor() as cursor:
            cursor.execute(
                "EXEC sp_SendMessage %s, %s, %s",
                [
                    form.cleaned_data["sender"].user_id,
                    form.cleaned_data["receiver"].user_id,
                    form.cleaned_data["content"],
                ],
            )

    def delete_model(self, request, obj):
        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM Messages WHERE message_id = %s", [obj.message_id]
            )


admin.site.register(Message, MessageAdmin)
