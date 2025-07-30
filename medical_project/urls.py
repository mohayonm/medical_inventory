from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('inventory.urls')),
    path('sales/', include('sales.urls')),
    path('shop/', include('shop.urls')),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)