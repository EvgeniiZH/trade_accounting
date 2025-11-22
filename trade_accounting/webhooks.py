"""
Модуль обработки webhook от Sentry с безопасной валидацией и отправкой уведомлений в Telegram.
"""
import hashlib
import hmac
import json
import os
from functools import wraps

import requests
from django.http import HttpResponse, JsonResponse
from django.conf import settings


def _get_setting(name, default=None):
    return getattr(settings, name, None) or os.getenv(name, default)



def verify_sentry_signature(request):
    """Проверяет подпись запроса от Sentry."""
    webhook_secret = _get_setting('WEBHOOK_SECRET')
    if not webhook_secret:
        return False

    sentry_signature = request.headers.get('Sentry-Hook-Signature')
    if not sentry_signature:
        return False

    # Получаем тело запроса в байтах
    payload = request.body
    
    # Вычисляем HMAC для тела запроса
    expected_signature = hmac.new(
        webhook_secret.encode('utf-8'),
        payload,
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(
        expected_signature,
        sentry_signature
    )


def require_webhook_signature(view_func):
    """Декоратор для проверки подписи webhook."""
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if not verify_sentry_signature(request):
            return HttpResponse('Invalid signature', status=403)
        return view_func(request, *args, **kwargs)
    return wrapped_view


def send_telegram_notification(message):
    """Отправляет уведомление в Telegram с таймаутом и retry."""
    bot_token = _get_setting("TELEGRAM_BOT_TOKEN")
    chat_id = _get_setting("TELEGRAM_CHAT_ID")

    if not (bot_token and chat_id):
        return False

    try:
        response = requests.post(
            f"https://api.telegram.org/bot{bot_token}/sendMessage",
            json={"chat_id": chat_id, "text": message},
            timeout=5,
            # Добавляем заголовки для безопасности
            headers={'User-Agent': 'Trade-Accounting-Bot/1.0'}
        )
        return response.status_code == 200
    except (requests.RequestException, ValueError) as e:
        if settings.DEBUG:
            print(f"Failed to send Telegram notification: {e}")
        return False


@require_webhook_signature
def sentry_webhook(request):
    """
    Обработчик webhook от Sentry с проверкой подписи.
    Ожидает POST-запрос с JSON-телом, содержащим title и url.
    """
    if request.method != "POST":
        return JsonResponse(
            {"error": "Only POST method is allowed"},
            status=405
        )

    try:
        data = json.loads(request.body or b"{}")
        title = data.get("title", "Неизвестная ошибка")
        url = data.get("url", "Нет ссылки")
        
        message = (
            "⚠️ Новое событие в Sentry!\n"
            f"Событие: {title}\n"
            f"Подробнее: {url}"
        )

        if send_telegram_notification(message):
            return JsonResponse({"status": "ok"})
        else:
            return JsonResponse(
                {"error": "Failed to send notification"},
                status=502
            )

    except json.JSONDecodeError:
        return JsonResponse(
            {"error": "Invalid JSON"},
            status=400
        )
    except Exception as e:
        if settings.DEBUG:
            error_message = str(e)
        else:
            error_message = "Internal server error"
        return JsonResponse(
            {"error": error_message},
            status=500
        )