from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone


class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    user_id = models.AutoField(primary_key=True, db_column="user_id")
    username = models.CharField(max_length=50, unique=True, db_column="username")
    email = models.CharField(max_length=100, unique=True, db_column="email")
    password_hash = models.CharField(max_length=255, db_column="password_hash")
    full_name = models.CharField(
        max_length=100, blank=True, null=True, db_column="full_name"
    )
    picture_url = models.CharField(
        max_length=255, blank=True, null=True, db_column="picture_url"
    )
    created_at = models.DateTimeField(default=timezone.now, db_column="created_at")
    last_login = models.DateTimeField(null=True, blank=True, db_column="last_login")

    def save(self, *args, **kwargs):
        # Prevent last_login from being automatically updated
        if "update_fields" in kwargs and "last_login" in kwargs["update_fields"]:
            kwargs["update_fields"].remove("last_login")
        super().save(*args, **kwargs)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        db_table = "Users"
        managed = False

    def __str__(self):
        return self.username

    # Map Django's password field to your password_hash
    @property
    def password(self):
        return self.password_hash

    @password.setter
    def password(self, raw_password):
        self.password_hash = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password_hash)

    # Disable last_login updates
    def save(self, *args, **kwargs):
        if "update_fields" in kwargs and "last_login" in kwargs["update_fields"]:
            kwargs["update_fields"].remove("last_login")
        super().save(*args, **kwargs)
