from django.contrib import admin
from django import forms
from django.contrib.auth.hashers import make_password
from .models import User

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=False)
    
    class Meta:
        model = User
        fields = ["username", "email", "full_name", "password"]  # Removed 'bio' since it's not in your model

class UserAdmin(admin.ModelAdmin):
    form = UserForm
    list_display = ("user_id", "username", "email", "full_name", "created_at")
    search_fields = ("username", "email")
    
    def save_model(self, request, obj, form, change):
        if form.cleaned_data["password"]:
            obj.password_hash = make_password(form.cleaned_data["password"])
        super().save_model(request, obj, form, change)

admin.site.register(User, UserAdmin)