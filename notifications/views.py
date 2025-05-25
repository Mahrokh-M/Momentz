from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db import connection
from django.contrib import messages


@login_required
def notifications(request):
    user_id = request.user.user_id
    if request.method == "POST":
        # Mark all notifications as read
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "EXEC sp_MarkNotificationsAsRead @userId = %s", [user_id]
                )
                messages.success(request, "All notifications marked as read.")
        except Exception as e:
            messages.error(request, f"Error marking notifications as read: {str(e)}")
        return redirect("notifications:notifications")
    try:
        with connection.cursor() as cursor:
            # Fetch all notifications for the user (both read and unread)
            cursor.execute(
                """
                SELECT 
                    N.notification_id, N.user_id, N.related_user_id, N.related_post_id,
                    N.notification_type, N.content, N.created_at, N.is_read,
                    U.username AS related_user_username
                FROM Notifications N
                JOIN Users U ON U.user_id = N.related_user_id
                WHERE N.user_id = %s
                ORDER BY N.created_at DESC
                """,
                [user_id],
            )
            columns = [col[0] for col in cursor.description]
            notifications = [dict(zip(columns, row)) for row in cursor.fetchall()]
            # Fetch unread notifications count using the GetUnreadNotifications function
            cursor.execute(
                "SELECT COUNT(*) FROM dbo.GetUnreadNotifications(%s)", [user_id]
            )
            unread_count = cursor.fetchone()[0]
        return render(
            request,
            "notifications/notifications.html",
            {
                "notifications": notifications,
                "unread_count": unread_count,
            },
        )
    except Exception as e:
        messages.error(request, f"Error loading notifications: {str(e)}")
        return render(
            request,
            "notifications/notifications.html",
            {
                "notifications": [],
                "unread_count": 0,
            },
        )
