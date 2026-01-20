from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Notification, NotificationPreference, User, UserProfile


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ["username", "email", "first_name", "last_name", "user_type", "is_active"]
    list_filter = ["user_type", "is_active", "is_staff", "date_joined"]
    search_fields = ["username", "email", "first_name", "last_name"]
    ordering = ["-date_joined"]

    fieldsets = UserAdmin.fieldsets + (
        (
            "Additional Info",
            {
                "fields": (
                    "user_type",
                    "phone_number",
                    "date_of_birth",
                    "address",
                    "city",
                    "state",
                    "zip_code",
                    "is_verified",
                    "is_email_verified",
                    "two_factor_enabled",
                )
            },
        ),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "Additional Info",
            {
                "fields": (
                    "user_type",
                    "phone_number",
                    "date_of_birth",
                    "address",
                    "city",
                    "state",
                    "zip_code",
                    "is_verified",
                    "is_email_verified",
                    "two_factor_enabled",
                )
            },
        ),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "company_name", "website"]
    search_fields = ["user__username", "company_name"]
    ordering = ["user__username"]


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ["user", "notification_type", "title", "priority", "is_read", "created_at"]
    list_filter = ["notification_type", "priority", "is_read", "is_archived", "created_at"]
    search_fields = ["user__username", "title", "message"]
    ordering = ["-created_at"]
    readonly_fields = ["id", "created_at", "updated_at"]

    actions = ["mark_as_read", "archive_notifications"]

    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f"{updated} notifications marked as read.")

    mark_as_read.short_description = "Mark selected notifications as read"

    def archive_notifications(self, request, queryset):
        updated = queryset.update(is_archived=True)
        self.message_user(request, f"{updated} notifications archived.")

    archive_notifications.short_description = "Archive selected notifications"


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ["user", "email_enabled", "in_app_enabled", "push_enabled", "digest_frequency"]
    list_filter = ["email_enabled", "in_app_enabled", "push_enabled", "digest_frequency"]
    search_fields = ["user__username"]
    ordering = ["user__username"]
