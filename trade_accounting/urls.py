from django.conf import settings
from django.contrib import admin
from django.template.context_processors import static
from django.conf.urls.static import static
from django.urls import path, include


def trigger_error(request):
    division_by_zero = 1 / 0  # Это вызовет ошибку 500


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('trades.urls')),  # Подключение приложения trades
    path('sentry-debug/', trigger_error),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
