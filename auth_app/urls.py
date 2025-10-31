from django.urls import path
from .views import RegisterAPI, LoginAPI, LogoutAPI, UserListAPI, UserDetailAPI,UserProfileAPI

urlpatterns = [
    path('register/', RegisterAPI.as_view(), name='register'),
    path('login/', LoginAPI.as_view(), name='login'),
    # path('facelogin/', FaceLoginAPI.as_view(), name='facelogin'),  
    path('logout/', LogoutAPI.as_view(), name='logout'),
    path('profile/', UserProfileAPI.as_view(), name='user-profile'),
    path('users/', UserListAPI.as_view(), name='user-list'),
    path('users/<int:pk>/', UserDetailAPI.as_view(), name='user-detail'),
]
