from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'is_client', 'is_admin', 'is_staff']

admin.site.register(CustomUser, CustomUserAdmin)
