# admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, Preferences, Services, Idtype, Agent


class CustomUserAdmin(BaseUserAdmin):
    ordering = ['id']
    list_display = ['email', 'first_name', 'last_name', 'phone_number', 'user_type', 'otp', 'account_completed', 'is_staff', 'is_active', 'is_superuser']

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal Info'), {'fields': ('first_name', 'last_name', 'phone_number', 'user_type', 'otp', 'is_agent', 'is_customer')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'account_completed', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        (_('Location'), {'fields': ('current_long','current_lat', 'current_location')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )


class AgentAdmin(admin.ModelAdmin):
    list_display = ['user', 'country', 'preference', 'id_type']

    fieldsets = (
        (None, {'fields': ('user', 'country', 'preference', 'id_type')}),
        ('Services', {'fields': ('services',)}),
        ('Document', {'fields': ('id_file',)}),
    )
    filter_horizontal = ('services',)


admin.site.register(User, CustomUserAdmin)
admin.site.register(Preferences)
admin.site.register(Services)
admin.site.register(Idtype)
admin.site.register(Agent, AgentAdmin)

