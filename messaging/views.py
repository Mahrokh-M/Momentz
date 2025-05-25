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
            SELECT DISTINCT
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
            WHERE (m.sender_id != %s OR m.receiver_id != %s)
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
        return redirect("messaging:inbox")

    # Get messages between these two users
    messages_list = (
        Message.objects.filter(
            (
                models.Q(sender_id=user_id, receiver_id=receiver.user_id)
                | models.Q(sender_id=receiver.user_id, receiver_id=user_id)
            )
        )
        .select_related("sender", "receiver")
        .order_by("sent_at")
    )

    # Mark unread messages as read
    Message.objects.filter(
        receiver_id=user_id, sender_id=receiver.user_id, is_read=False
    ).update(is_read=True)

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
        # Get data from request
        data = json.loads(request.body)
        receiver_id = data.get("receiver_id")
        content = data.get("content")
        sender_id = request.user.user_id

        # Validate input
        if not content or not receiver_id:
            return JsonResponse(
                {"status": "error", "message": "Missing required fields"}, status=400
            )

        logger.info(f"Sending message from {sender_id} to {receiver_id}")

        with connection.cursor() as cursor:
            try:
                # Execute stored procedure
                cursor.execute(
                    "EXEC sp_SendMessage @senderId=%s, @receiverId=%s, @content=%s",
                    [sender_id, receiver_id, content],
                )

                # Verify the message was inserted
                cursor.execute(
                    """SELECT TOP 1 message_id, sent_at, content 
                       FROM Messages 
                       WHERE sender_id = %s AND receiver_id = %s 
                       ORDER BY sent_at DESC""",
                    [sender_id, receiver_id],
                )

                row = cursor.fetchone()
                if not row:
                    return JsonResponse(
                        {"status": "error", "message": "Message not created"},
                        status=500,
                    )

                # Get sender info
                sender = User.objects.get(user_id=sender_id)

                return JsonResponse(
                    {
                        "status": "success",
                        "message": {
                            "content": row[2],  # content from the query
                            "sent_at": row[1].isoformat(),  # sent_at from the query
                            "message_id": row[0],  # message_id from the query
                            "sender_id": sender_id,
                            "receiver_id": receiver_id,
                            "sender_picture_url": sender.picture_url or "",
                        },
                    }
                )

            except Exception as e:
                logger.error(f"Database error in send_message: {str(e)}")
                return JsonResponse(
                    {"status": "error", "message": "Database operation failed"},
                    status=500,
                )

    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)
    except Exception as e:
        logger.error(f"Unexpected error in send_message: {str(e)}")
        return JsonResponse(
            {"status": "error", "message": "Internal server error"}, status=500
        )


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
