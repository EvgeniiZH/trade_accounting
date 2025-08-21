# trade_accounting/urls.py
from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import os
import requests

def healthz(_request):
    # Лёгкий healthcheck без БД
    return HttpResponse("ok", content_type="text/plain")

def trigger_error(_request):
    # Тестовая ошибка для проверки Sentry
    _ = 1 / 0
    return HttpResponse("never here")

@csrf_exempt
def sentry_webhook(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)

    try:
        data = json.loads(request.body or b"{}")
        title = data.get("title", "Неизвестная ошибка")
        url = data.get("url", "Нет ссылки")
        message = f"🚨 Ошибка в Sentry!\n🔹 {title}\n🔗 {url}"

        # Токен и чат берём из ENV (см. ниже .env.production)
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        chat_id = os.getenv("TELEGRAM_CHAT_ID")

        if bot_token and chat_id:
            requests.post(
                f"https://api.telegram.org/bot{bot_token}/sendMessage",
                data={"chat_id": chat_id, "text": message},
                timeout=5,
            )

        return JsonResponse({"status": "ok"})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

urlpatterns = [
    path("healthz", healthz),               # ✅ для docker healthcheck
    path("admin/", admin.site.urls),
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
