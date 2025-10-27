from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # Champs affichés dans la liste
    list_display = ("username", "email", "CIN", "phone", "is_staff", "is_active")
    search_fields = ("username", "email", "CIN", "phone")
    list_filter = ("is_staff", "is_active")

    # Champs affichés dans le formulaire d’édition
    fieldsets = (
        ("Personal Info", {
            "fields": ("username", "first_name", "last_name", "email", "CIN", "phone", "image")
        }),
        ("Permissions", {
            "fields": ("is_active", "is_staff", "user_permissions")
        }),
        ("Important dates", {
            "fields": ("last_login", "date_joined")
        }),
    )

    # Champs visibles à la création d’un nouvel utilisateur
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("username", "password1", "password2", "email", "CIN", "phone", "image", "is_staff", "is_active"),
        }),
    )

    ordering = ("username",)
