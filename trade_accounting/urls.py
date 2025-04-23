from django.conf import settings
from django.contrib import admin
from django.conf.urls.static import static
from django.urls import path, include
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import requests
from django.conf import settings
from django.conf.urls.static import static


def trigger_error(request):
    division_by_zero = 1 / 0  # Это вызовет ошибку 500


@csrf_exempt
def sentry_webhook(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            title = data.get("title", "Неизвестная ошибка")
            url = data.get("url", "Нет ссылки")
            message = f"🚨 Ошибка в Sentry!\n🔹 {title}\n🔗 {url}"

            # Отправляем сообщение в Telegram
            requests.post(
                "https://api.telegram.org/bot7713729563:AAG3tH6zlVIGw6GtBUAyQpwrmcRL1ZwYwdk/sendMessage",
                data={"chat_id": "-1002364844069", "text": message},
            )

            return JsonResponse({"status": "ok"})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request"}, status=400)


urlpatterns = [
    path("webhook/sentry/", sentry_webhook),  # Webhook для Sentry
    path('admin/', admin.site.urls),
    path('', include('trades.urls')),  # Подключение приложения trades
    path('sentry-debug/', trigger_error),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)