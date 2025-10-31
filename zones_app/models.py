from django.db import models
from django.conf import settings

class Zone(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Location data
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    zone_type = models.CharField(max_length=100, null=True, blank=True)
    
    # Nearby places (stored as JSON array)
    nearby_places = models.JSONField(default=list, blank=True)
    
    # AI recommendations (stored as JSON array)
    recommendations = models.JSONField(default=list, blank=True)
    
    # Relations
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='zones'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Zone Sensible"
        verbose_name_plural = "Zones Sensibles"
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['zone_type']),
        ]


class ZoneAlert(models.Model):
    """Alertes associées aux zones"""
    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, related_name='alerts')
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    message = models.TextField()
    detected_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resolved_alerts'
    )
    
    def __str__(self):
        return f"{self.zone.name} - {self.severity} - {self.detected_at.strftime('%Y-%m-%d %H:%M')}"
    
    class Meta:
        ordering = ['-detected_at']
        verbose_name = "Zone Alert"
        verbose_name_plural = "Zone Alerts"
        indexes = [
            models.Index(fields=['-detected_at']),
            models.Index(fields=['severity']),
            models.Index(fields=['is_resolved']),
        ]