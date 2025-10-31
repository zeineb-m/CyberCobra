from django.contrib import admin
from .models import Equipement


@admin.register(Equipement)
class EquipementAdmin(admin.ModelAdmin):
    list_display = ("id_equipement", "nom", "statut", "date_ajout")
    list_filter = ("statut", "date_ajout")
    search_fields = ("nom", "description")
