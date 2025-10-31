from django.urls import path
from . import views

#URLConf
urlpatterns = [
    path('get/', views.get_reports),
    path('create/', views.create_report ),
    path('<int:pk>/', views.specific_report),
    path('summarize/', views.summarize_report)
    

]