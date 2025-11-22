from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

# -*- coding: utf-8 -*-

class UsernameOrEmailBackend(ModelBackend):
    """Позволяет входить по имени пользователя ИЛИ по e‑mail (без учёта регистра).
    Не меняет проверки пароля/активности — делегирует ModelBackend.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None
        User = get_user_model()
        try:
            user = User.objects.get(
                Q(username__iexact=username) | Q(email__iexact=username)
            )
        except User.DoesNotExist:
            return None
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
