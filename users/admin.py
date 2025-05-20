# admin.py
from django.contrib import admin
from django.contrib.auth.hashers import make_password
from django import forms
from .models import User


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=False)

    class Meta:
        model = User
        fields = ["username", "email", "full_name", "bio", "password"]


class UserAdmin(admin.ModelAdmin):
    list_display = ("user_id", "username", "email", "full_name", "created_at")
    search_fields = ("username", "email")
    list_filter = ("created_at",)
    form = UserForm

    def save_model(self, request, obj, form, change):
        if form.cleaned_data["password"]:
            obj.password_hash = make_password(form.cleaned_data["password"])
        super().save_model(request, obj, form, change)


admin.site.register(User, UserAdmin)
