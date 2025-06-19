from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):

    fieldsets = UserAdmin.fieldsets + ((None, {'fields': ('birth_date', 'is_premium')}),
    )

    add_fieldsets = UserAdmin.add_fieldsets + ((None, {'fields': ('birth_date', 'is_premium')}),
    )

    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'is_premium']
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_premium')
