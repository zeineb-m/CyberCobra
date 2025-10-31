from rest_framework import serializers
from .models import Camera


class CameraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Camera
        fields = [
            'id_camera',
            'name',
            'zone',
            'ip_address',
            'resolution',
            'status',
            'date_ajout',
        ]
        read_only_fields = ['id_camera', 'date_ajout']
