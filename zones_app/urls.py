from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ZoneViewSet, ZoneAlertViewSet

router = DefaultRouter()
router.register(r'zones', ZoneViewSet, basename='zone')
router.register(r'alerts', ZoneAlertViewSet, basename='alert')

urlpatterns = [
    path('', include(router.urls)),
]
