# trade_accounting/urls.py
from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse

from .webhooks import sentry_webhook

def healthz(_request):
    # Лёгкий healthcheck без БД
    return HttpResponse("ok", content_type="text/plain")

def trigger_error(_request):
    # Тестовая ошибка для проверки Sentry
    _ = 1 / 0
    return HttpResponse("never here")

urlpatterns = [
    path("healthz", healthz),               # ✅ для docker healthcheck
    path("admin/", admin.site.urls),
    path("api/", include("trade_accounting.api_urls")), # API endpoint
    path("", include("trades.urls")),
    path("sentry-debug/", trigger_error),

    # Лучше сделать «секретный» путь для вебхука:
    path("webhook/sentry/sentry-webhook-4f7a2c6e/", sentry_webhook),
]

# Раздача статики/медиа в DEBUG
if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
