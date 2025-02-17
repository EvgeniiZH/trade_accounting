from django.shortcuts import redirect
from django.conf import settings

class LoginRequiredMiddleware:
    """
    Перенаправляет неавторизованных пользователей на страницу входа,
    за исключением URL, связанных с аутентификацией или статическими файлами.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Список URL, которые не требуют аутентификации
        exempt_urls = [settings.LOGIN_URL, '/admin/', '/static/']

        if not request.user.is_authenticated:
            # Если запрошенный URL не входит в список exempt_urls
            if not any(request.path.startswith(url) for url in exempt_urls):
                return redirect(settings.LOGIN_URL)
        return self.get_response(request)
