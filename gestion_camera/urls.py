from django.urls import path
from .views import (
    CameraListCreateAPIView,
    CameraDetailAPIView,
    FireDetectionAPIView,
    FireDetectionHeuristicAPIView
)


urlpatterns = [
    path('cameras/', CameraListCreateAPIView.as_view(), name='camera-list-create'),
    path('cameras/<int:pk>/', CameraDetailAPIView.as_view(), name='camera-detail'),
    path('cameras/detect-fire/', FireDetectionAPIView.as_view(), name='fire-detection'),
    path('cameras/detect-fire-heuristic/', FireDetectionHeuristicAPIView.as_view(), name='fire-detection-heuristic'),
]
