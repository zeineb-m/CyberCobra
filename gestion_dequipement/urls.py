from django.urls import path
from .views import (
    EquipementListCreateAPIView,
    EquipementDetailAPIView,
    EquipementRecognizeAPIView
)


urlpatterns = [
    path('equipements/', EquipementListCreateAPIView.as_view(), name='equipement-list-create'),
    path('equipements/<int:pk>/', EquipementDetailAPIView.as_view(), name='equipement-detail'),
    path('equipements/recognize/', EquipementRecognizeAPIView.as_view(), name='equipement-recognize'),
]
