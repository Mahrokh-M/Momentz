import logging
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.db import connection
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from .models import Message
from users.models import User
from django.db import models
import json

logger = logging.getLogger(__name__)


@login_required
def inbox(request):
    user_id = request.user.user_id
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT 
                CASE 
                    WHEN m.sender_id = %s THEN m.receiver_id 
                    ELSE m.sender_id 
                END AS chat_partner_id,
                u.username AS chat_partner_username,
                u.picture_url AS chat_partner_picture_url,
                m.content,
                m.sent_at,
                m.is_read,
                m.sender_id,
                m.receiver_id
            FROM dbo.GetLastMessages(%s) m
            JOIN Users u ON (
                CASE 
                    WHEN m.sender_id = %s THEN m.receiver_id 
                    ELSE m.sender_id 
                END = u.user_id
            )
            WHERE m.sender_id != %s OR m.receiver_id != %s
            ORDER BY m.sent_at DESC
        """,
            [user_id, user_id, user_id, user_id, user_id],
        )
        columns = [col[0] for col in cursor.description]
        conversations = [dict(zip(columns, row)) for row in cursor.fetchall()]

    conversations = [
        conv for conv in conversations if conv.get("chat_partner_username")
    ]

    all_users = User.objects.exclude(user_id=user_id).values(
        "username", "user_id", "picture_url"
    )

    return render(
        request,
        "messaging/inbox.html",
        {
            "conversations": conversations,
            "all_users": all_users,
        },
    )


@login_required
def chat(request, username):
    user_id = request.user.user_id
    try:
        receiver = User.objects.get(username=username)
    except User.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect("inbox")

    messages_list = (
        Message.objects.filter(
            models.Q(sender_id=user_id, receiver_id=receiver.user_id)
            | models.Q(sender_id=receiver.user_id, receiver_id=user_id)
        )
        .select_related("sender", "receiver")
        .order_by("sent_at")
    )

    if not messages_list.exists() and request.method == "GET":
        messages.info(request, "No messages yet. Start a conversation!")

    # Mark unread messages from the receiver as read
    unread_messages = messages_list.filter(
        receiver_id=user_id, sender_id=receiver.user_id, is_read=False
    )
    for message in unread_messages:
        message.is_read = True
        message.save()

    return render(
        request,
        "messaging/chat.html",
        {
            "receiver_username": username,
            "receiver_id": receiver.user_id,
            "receiver_picture_url": receiver.picture_url,
            "messages": messages_list,
            "user_id": user_id,
            "user_picture_url": request.user.picture_url,
        },
    )


@login_required
@require_POST
def send_message(request):
    try:
        data = json.loads(request.body)
        receiver_id = data.get("receiver_id")
        content = data.get("content")
        sender_id = request.user.user_id

        logger.info(
            f"Sending message: sender={sender_id}, receiver={receiver_id}, content={content}"
        )
        with connection.cursor() as cursor:
            cursor.execute(
                "EXEC sp_SendMessage @senderId=%s, @receiverId=%s, @content=%s",
                [sender_id, receiver_id, content],
            )
            cursor.execute(
                "SELECT TOP 1 message_id, sent_at FROM Messages WHERE sender_id = %s AND receiver_id = %s ORDER BY sent_at DESC",
                [sender_id, receiver_id],
            )
            new_message = dict(zip(["message_id", "sent_at"], cursor.fetchone()))

            sender = User.objects.get(user_id=sender_id)
            return JsonResponse(
                {
                    "status": "success",
                    "message": {
                        "content": content,
                        "sent_at": new_message["sent_at"].isoformat(),
                        "message_id": new_message["message_id"],
                        "sender_id": sender_id,
                        "receiver_id": receiver_id,
                        "sender_picture_url": sender.picture_url,
                    },
                }
            )
    except Exception as e:
        logger.error(f"Error in send_message: {str(e)}")
        return JsonResponse({"status": "error", "message": str(e)}, status=400)


@login_required
@require_POST
def mark_message_read(request, message_id):
    try:
        message = Message.objects.get(
            message_id=message_id, receiver_id=request.user.user_id
        )
        message.is_read = True
        message.save()
        return JsonResponse({"status": "success", "message": "Message marked as read."})
    except Message.DoesNotExist:
        return JsonResponse(
            {"status": "error", "message": "Message not found or not yours."},
            status=404,
        )
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=400)
