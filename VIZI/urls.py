from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
    path('admin/', admin.site.urls),
    path('', include('main.urls')),           # URL вашего магазина
    path('analytics/', include('analytics.urls')),  # URL аналитики
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)