from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponseRedirect
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('auth_app.urls')),
    path('report/', include('report.urls')),
    path('api/', include('gestion_dequipement.urls')),
    path('api/', include('gestion_camera.urls')),
    path('api/', include('zones_app.urls')),
 path('', lambda request: HttpResponseRedirect('https://cybercobra-2.onrender.com/')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
