from rest_framework import serializers
from .models import Equipement


class EquipementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipement
        fields = [
            'id_equipement',
            'nom',
            'statut',
            'date_ajout',
            'description',
            'image',
            'image_hash',
            'phash',
        ]
        read_only_fields = ['id_equipement', 'date_ajout', 'image_hash', 'phash']
        read_only_fields = ['id_equipement', 'date_ajout']
