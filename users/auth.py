from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.hashers import check_password
from django.db import connection
from .models import User

class SQLServerAuthBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            with connection.cursor() as cursor:
                
                cursor.execute(
                    "SELECT user_id, password_hash FROM Users WHERE username = %s", 
                    [username]
                )
                row = cursor.fetchone()
                
                if row:
                    user_id, db_password = row
                    if check_password(password, db_password):
                        user = User.objects.get(user_id=user_id)
                        # Prevent last_login update
                        user.save(update_fields=[])
                        return user
        except Exception as e:
            print(f"Auth error: {e}")
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return None