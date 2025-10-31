from django.contrib import admin
from django.utils.html import format_html
from .models import Zone, ZoneAlert


@admin.register(Zone)
class ZoneAdmin(admin.ModelAdmin):
    list_display = ['name', 'status_badge', 'zone_type', 'alert_count', 'recommendation_count', 'address_short', 'created_at']
    list_filter = ['status', 'zone_type', 'created_at', 'updated_at']
    search_fields = ['name', 'description', 'address', 'zone_type']
    readonly_fields = ['created_at', 'updated_at', 'created_by']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'status', 'zone_type')
        }),
        ('Location', {
            'fields': ('latitude', 'longitude', 'address')
        }),
        ('Data', {
            'fields': ('nearby_places', 'recommendations'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def status_badge(self, obj):
        colors = {'active': 'green', 'inactive': 'gray'}
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color, obj.status.upper()
        )
    status_badge.short_description = 'Status'
    
    def alert_count(self, obj):
        count = obj.alerts.filter(is_resolved=False).count()
        if count > 0:
            return format_html('<span style="color: red; font-weight: bold;">{}</span>', count)
        return count
    alert_count.short_description = 'Active Alerts'
    
    def recommendation_count(self, obj):
        return len(obj.recommendations) if obj.recommendations else 0
    recommendation_count.short_description = 'Recommendations'
    
    def address_short(self, obj):
        if obj.address and len(obj.address) > 50:
            return obj.address[:50] + '...'
        return obj.address or '-'
    address_short.short_description = 'Address'
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(ZoneAlert)
class ZoneAlertAdmin(admin.ModelAdmin):
    list_display = ['zone', 'severity_badge', 'message_short', 'detected_at', 'is_resolved_badge', 'resolved_by']
    list_filter = ['severity', 'is_resolved', 'detected_at']
    search_fields = ['zone__name', 'message']
    readonly_fields = ['detected_at', 'resolved_at']
    
    def severity_badge(self, obj):
        colors = {'low': '#10b981', 'medium': '#f59e0b', 'high': '#ef4444', 'critical': '#7f1d1d'}
        color = colors.get(obj.severity, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            color, obj.severity.upper()
        )
    severity_badge.short_description = 'Severity'
    
    def is_resolved_badge(self, obj):
        if obj.is_resolved:
            return format_html('<span style="color: green;">✓ Resolved</span>')
        return format_html('<span style="color: red;">✗ Active</span>')
    is_resolved_badge.short_description = 'Status'
    
    def message_short(self, obj):
        if len(obj.message) > 60:
            return obj.message[:60] + '...'
        return obj.message
    message_short.short_description = 'Message'
    
    actions = ['mark_as_resolved', 'mark_as_unresolved']
    
    def mark_as_resolved(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(is_resolved=True, resolved_at=timezone.now(), resolved_by=request.user)
        self.message_user(request, f'{updated} alert(s) marked as resolved.')
    mark_as_resolved.short_description = 'Mark selected alerts as resolved'
    
    def mark_as_unresolved(self, request, queryset):
        updated = queryset.update(is_resolved=False, resolved_at=None, resolved_by=None)
        self.message_user(request, f'{updated} alert(s) marked as unresolved.')
    mark_as_unresolved.short_description = 'Mark selected alerts as unresolved'


