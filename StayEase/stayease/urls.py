from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
import os

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),   
    path('accounts/', include('allauth.urls')),
    path('properties/', include('properties.urls')),
    path("bookings/", include("bookings.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Vercel runs with DEBUG=False; add media serving route for uploaded images.
if os.getenv("VERCEL") == "1":
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
