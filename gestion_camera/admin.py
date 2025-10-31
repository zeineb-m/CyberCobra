from django.contrib import admin
from .models import Camera


@admin.register(Camera)
class CameraAdmin(admin.ModelAdmin):
    list_display = ("id_camera", "name", "zone", "ip_address", "resolution", "status", "date_ajout")
    list_filter = ("status", "zone", "date_ajout")
    search_fields = ("name", "zone", "ip_address")
