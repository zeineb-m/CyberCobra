from rest_framework import serializers
from .models import Zone, ZoneAlert


class ZoneAlertSerializer(serializers.ModelSerializer):
    zone_name = serializers.CharField(source='zone.name', read_only=True)
    
    class Meta:
        model = ZoneAlert
        fields = ['id', 'zone', 'zone_name', 'severity', 'message', 'detected_at', 'is_resolved']
        read_only_fields = ['id', 'detected_at']


class ZoneSerializer(serializers.ModelSerializer):
    # Frontend expects these exact field names (camelCase)
    location = serializers.SerializerMethodField()
    zoneType = serializers.CharField(source='zone_type', required=False, allow_blank=True, allow_null=True)
    nearbyPlaces = serializers.JSONField(source='nearby_places', required=False, default=list)
    
    # Additional fields
    alerts = ZoneAlertSerializer(many=True, read_only=True)
    alert_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Zone
        fields = [
            'id', 'name', 'description', 'status', 
            'latitude', 'longitude', 'location', 'address', 
            'zoneType', 'nearbyPlaces', 'recommendations', 
            'alerts', 'alert_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_location(self, obj):
        """Return location in format expected by frontend: {lat, lng}"""
        if obj.latitude is not None and obj.longitude is not None:
            return {
                'lat': float(obj.latitude),
                'lng': float(obj.longitude)
            }
        return None
    
    def get_alert_count(self, obj):
        """Return count of unresolved alerts"""
        return obj.alerts.filter(is_resolved=False).count()
    
    def validate_recommendations(self, value):
        """Ensure recommendations is always a list"""
        if value is None:
            return []
        if isinstance(value, str):
            try:
                import json
                value = json.loads(value)
            except:
                return []
        if not isinstance(value, list):
            return []
        return value
    
    def validate_nearby_places(self, value):
        """Ensure nearby_places is always a list"""
        if value is None:
            return []
        if isinstance(value, str):
            try:
                import json
                value = json.loads(value)
            except:
                return []
        if not isinstance(value, list):
            return []
        return value
    
    def create(self, validated_data):
        """Handle creation with user association"""
        # Associate user if authenticated
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            validated_data['created_by'] = request.user
        
        # Ensure JSON fields are lists
        if 'recommendations' not in validated_data:
            validated_data['recommendations'] = []
        if 'nearby_places' not in validated_data:
            validated_data['nearby_places'] = []
            
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """Handle updates"""
        # Ensure JSON fields are lists
        if 'recommendations' in validated_data and validated_data['recommendations'] is None:
            validated_data['recommendations'] = []
        if 'nearby_places' in validated_data and validated_data['nearby_places'] is None:
            validated_data['nearby_places'] = []
            
        return super().update(instance, validated_data)
    
    def to_representation(self, instance):
        """Customize output format"""
        data = super().to_representation(instance)
        
        # Ensure recommendations is always a list
        if data.get('recommendations') is None:
            data['recommendations'] = []
        
        # Ensure nearbyPlaces is always a list
        if data.get('nearbyPlaces') is None:
            data['nearbyPlaces'] = []
        
        return data
