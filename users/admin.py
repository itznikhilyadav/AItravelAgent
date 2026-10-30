from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = (
        'id',
        'username',
        'email',
        'is_staff',
        'is_active',
    )

    search_fields = ('username', 'email')
    list_filter = ('is_staff', 'is_active')