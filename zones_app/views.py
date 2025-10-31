from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Q
from .models import Zone, ZoneAlert
from .serializers import ZoneSerializer, ZoneAlertSerializer
from .services import get_security_recommendations


class ZoneViewSet(viewsets.ModelViewSet):
    queryset = Zone.objects.all()
    serializer_class = ZoneSerializer
    permission_classes = [AllowAny]  # Change to [IsAuthenticated] in production
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description', 'address']
    
    def get_queryset(self):
        queryset = Zone.objects.all().order_by('-created_at')
        
        # Filter by status
        status_param = self.request.query_params.get('status', None)
        if status_param:
            queryset = queryset.filter(status=status_param)
        
        # Search
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | 
                Q(description__icontains=search) |
                Q(address__icontains=search)
            )
        
        return queryset
    
    def create(self, request, *args, **kwargs):
        """Override create to handle frontend data structure"""
        data = request.data.copy()
        
        # Ensure recommendations is a list
        if 'recommendations' in data:
            if isinstance(data['recommendations'], str):
                try:
                    import json
                    data['recommendations'] = json.loads(data['recommendations'])
                except:
                    data['recommendations'] = []
        
        # Ensure nearby_places is a list
        if 'nearby_places' in data:
            if isinstance(data['nearby_places'], str):
                try:
                    import json
                    data['nearby_places'] = json.loads(data['nearby_places'])
                except:
                    data['nearby_places'] = []
        
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def update(self, request, *args, **kwargs):
        """Override update to handle frontend data structure"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        data = request.data.copy()
        
        # Ensure recommendations is a list
        if 'recommendations' in data:
            if isinstance(data['recommendations'], str):
                try:
                    import json
                    data['recommendations'] = json.loads(data['recommendations'])
                except:
                    data['recommendations'] = []
        
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response(serializer.data)
    
    @action(detail=True, methods=['patch'])
    def update_recommendations(self, request, pk=None):
        """Update only the recommendations"""
        zone = self.get_object()
        recommendations = request.data.get('recommendations', [])
        
        # Ensure it's a list
        if isinstance(recommendations, str):
            try:
                import json
                recommendations = json.loads(recommendations)
            except:
                recommendations = []
        
        zone.recommendations = recommendations
        zone.save()
        serializer = self.get_serializer(zone)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def create_alert(self, request, pk=None):
        """Create an alert for a zone"""
        zone = self.get_object()
        serializer = ZoneAlertSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(zone=zone)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def alerts(self, request, pk=None):
        """Get all alerts for a zone"""
        zone = self.get_object()
        alerts = zone.alerts.all()
        serializer = ZoneAlertSerializer(alerts, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Global zone statistics"""
        total_zones = Zone.objects.count()
        active_zones = Zone.objects.filter(status='active').count()
        inactive_zones = Zone.objects.filter(status='inactive').count()
        total_alerts = ZoneAlert.objects.filter(is_resolved=False).count()
        
        return Response({
            'total_zones': total_zones,
            'active_zones': active_zones,
            'inactive_zones': inactive_zones,
            'unresolved_alerts': total_alerts
        })
    
    @action(detail=False, methods=['post'])
    def get_recommendations(self, request):
        """Get AI security recommendations for an address"""
        address = request.data.get('address', '')
        zone_type = request.data.get('zone_type', '')
        nearby_places = request.data.get('nearby_places', [])
        
        if not address:
            return Response(
                {'error': 'Address is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        recommendations = get_security_recommendations(address, zone_type, nearby_places)
        
        return Response({
            'recommendations': recommendations,
            'address': address
        })


class ZoneAlertViewSet(viewsets.ModelViewSet):
    queryset = ZoneAlert.objects.all()
    serializer_class = ZoneAlertSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        queryset = ZoneAlert.objects.all().order_by('-detected_at')
        
        # Filter by zone
        zone_id = self.request.query_params.get('zone', None)
        if zone_id:
            queryset = queryset.filter(zone_id=zone_id)
        
        # Filter by resolved status
        is_resolved = self.request.query_params.get('is_resolved', None)
        if is_resolved is not None:
            queryset = queryset.filter(is_resolved=is_resolved.lower() == 'true')
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Mark an alert as resolved"""
        alert = self.get_object()
        alert.is_resolved = True
        alert.save()
        serializer = self.get_serializer(alert)
        return Response(serializer.data)


