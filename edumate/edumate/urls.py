
from django.contrib import admin
from django.urls import path, include

from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from apps.common.views import redirector

urlpatterns = [
    path("", redirector, name="root"),
    
    path('admin/', admin.site.urls),
    
    path('auth/', include('apps.authentication.urls')),
    path('users/', include('apps.users.urls')),
    
    
    
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    # Optional UI:
    path('api/info/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/docs/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
