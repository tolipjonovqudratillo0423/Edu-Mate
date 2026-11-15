from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from apps.common.views import redirector
from apps.goals.views import AvailabilityListCreateView, AvailabilityDetailView

urlpatterns = [
    path("", redirector, name="root"),
    
    path('admin/', admin.site.urls),
    
    path('auth/', include('apps.authentication.urls')),
    path('users/', include('apps.users.urls')),
    path('goals/', include('apps.goals.urls')),
    path('catalog/', include('apps.catalog.urls')),
    path('tracks/', include('apps.catalog.urls')),
    path('availability/', AvailabilityListCreateView.as_view(), name='availability-root'),
    path('availability/<int:pk>/', AvailabilityDetailView.as_view(), name='availability-root-detail'),
    path('matching/', include('apps.matching.urls')),
    path('', include('apps.matching.urls')),
    
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    # Optional UI:
    path('api/info/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/docs/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)  
    urlpatterns += [
        path('silk/', include('silk.urls', namespace='silk')),
    ]
