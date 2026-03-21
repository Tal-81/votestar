from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ['email']

    list_display = [
        'email',
        'first_name',
        'is_staff',
        'is_superuser',
        'is_active',
        'date_joined',
    ]

    list_filter = [
        'is_staff',
        'is_superuser',
        'is_active',
    ]

    search_fields = [
        'email',
        'first_name',
    ]

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (
            'Personal info',
            {'fields': ('first_name', 'last_name')},
        ),
        (
            'Permissions',
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                    'groups',
                    'user_permissions',
                )
            },
        ),
        (
            'Important dates',
            {'fields': ('last_login', 'date_joined')},
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': ('email', 'password1', 'password2'),
            },
        ),
    )

    def delete_model(self, request, obj):
        """Block deletion of any superuser account from the admin panel."""
        if obj.is_superuser:
            self.message_user(
                request,
                (
                    f'Cannot delete admin account "{obj.email}". '
                    'Admin accounts are protected.'
                ),
                level=messages.ERROR,
            )
            return
        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        """Block bulk deletion if any superuser is selected."""
        protected = queryset.filter(is_superuser=True)

        if protected.exists():
            emails = ', '.join(
                protected.values_list('email', flat=True)
            )

            self.message_user(
                request,
                (
                    f'Cannot delete admin account(s): {emails}. '
                    'Admin accounts are protected.'
                ),
                level=messages.ERROR,
            )

            queryset.filter(is_superuser=False).delete()
            return

        super().delete_queryset(request, queryset)

    def has_delete_permission(self, request, obj=None):
        """Hide the delete button entirely when viewing a superuser."""
        if obj is not None and obj.is_superuser:
            return False

        return super().has_delete_permission(request, obj)
