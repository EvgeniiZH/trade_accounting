from django.conf import settings
from django.contrib import admin
from django.template.context_processors import static
from django.conf.urls.static import static
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('trades.urls')),  # Подключение приложения trades
]


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)