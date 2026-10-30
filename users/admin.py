from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):

    list_display = (
        'id',
        'username',
        'email',
        'phone',
        'is_active',
        'is_staff',
        'date_joined',
    )

    search_fields = ('username', 'email', 'phone')

    list_filter = ('is_active', 'is_staff')

    ordering = ('-date_joined',)

    fieldsets = UserAdmin.fieldsets + (
        ('Additional Information', {
            'fields': ('phone', 'profile_picture'),
        }),
    )