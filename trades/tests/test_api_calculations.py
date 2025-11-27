import io
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse
from rest_framework.test import APIClient

from trades.models import Item, Calculation, CalculationItem


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    User = get_user_model()
    return User.objects.create_user(username="user", password="pass123")


@pytest.fixture
def admin(db):
    User = get_user_model()
    return User.objects.create_user(username="admin", password="pass123", is_superuser=True, is_admin=True)


@pytest.fixture
def sample_calculations(db, user, admin):
    """
    Создаём по одному расчёту для обычного пользователя и админа,
    чтобы проверить фильтрацию списка.
    """
    item = Item.objects.create(name="Тестовый товар", price=Decimal("10.00"))

    calc_user = Calculation.objects.create(user=user, title="Расчёт пользователя", markup=Decimal("0"))
    CalculationItem.objects.create(calculation=calc_user, item=item, quantity=1)
    calc_user.refresh_totals()

    calc_admin = Calculation.objects.create(user=admin, title="Расчёт админа", markup=Decimal("0"))
    CalculationItem.objects.create(calculation=calc_admin, item=item, quantity=2)
    calc_admin.refresh_totals()

    return {"user_calc": calc_user, "admin_calc": calc_admin}


@pytest.mark.django_db
def test_calculations_list_requires_auth(api_client):
    url = "/api/calculations/"
    response = api_client.get(url)
    # DRF по умолчанию отвечает 403, если нет сессии
    assert response.status_code in (401, 403)


@pytest.mark.django_db
def test_calculations_list_user_sees_only_own(api_client, user, sample_calculations):
    api_client.force_authenticate(user=user)
    response = api_client.get("/api/calculations/")
    assert response.status_code == 200
    titles = {c["title"] for c in response.data["results"]}
    assert "Расчёт пользователя" in titles
    # обычный пользователь не должен видеть расчёт админа
    assert "Расчёт админа" not in titles


@pytest.mark.django_db
def test_calculations_list_admin_sees_all(api_client, admin, sample_calculations):
    api_client.force_authenticate(user=admin)
    response = api_client.get("/api/calculations/")
    assert response.status_code == 200
    titles = {c["title"] for c in response.data["results"]}
    assert "Расчёт пользователя" in titles
    assert "Расчёт админа" in titles


@pytest.mark.django_db
def test_calculations_list_search_by_title(api_client, admin, sample_calculations):
    api_client.force_authenticate(user=admin)
    response = api_client.get("/api/calculations/", {"search": "пользователя"})
    assert response.status_code == 200
    titles = {c["title"] for c in response.data["results"]}
    assert titles == {"Расчёт пользователя"}


@pytest.mark.django_db
def test_export_calculations_zip_success(api_client, admin, sample_calculations):
    """
    Проверяем, что экспорт выбранных расчётов отдаёт zip-файл.
    Детальную структуру архива можно добавить позже, сейчас главное – стабильный ответ.
    """
    client = Client()
    client.force_login(admin)
    url = "/api/calculations/export/"
    ids = [sample_calculations["user_calc"].id, sample_calculations["admin_calc"].id]
    # view поддерживает и form-data, и JSON; для простоты шлём form-data
    response = client.post(url, {"ids": ids})

    assert response.status_code == 200
    # Django может отдавать разные заголовки, проверим по content-type и что это бинарь
    content_type = response["Content-Type"]
    assert "zip" in content_type or "application/octet-stream" in content_type
    assert isinstance(response.content, (bytes, bytearray))
    # На всякий случай убедимся, что ответ не пустой
    assert len(response.content) > 0


@pytest.mark.django_db
def test_export_calculations_without_ids_returns_400(api_client, admin):
    """
    Если не переданы ids, бэкенд должен вернуть 400 с понятным сообщением.
    """
    client = Client()
    client.force_login(admin)
    url = "/api/calculations/export/"
    response = client.post(url, {})

    assert response.status_code == 400


@pytest.mark.django_db
def test_export_calculations_user_cannot_export_foreign(api_client, user, admin, sample_calculations):
    """
    Обычный пользователь не должен экспортировать чужие расчёты.
    Если среди переданных id только чужие – 404.
    """
    client = Client()
    client.force_login(user)
    url = "/api/calculations/export/"
    foreign_id = sample_calculations["admin_calc"].id
    response = client.post(url, {"ids": [foreign_id]})

    assert response.status_code == 404


@pytest.mark.django_db
def test_export_calculations_user_exports_only_own_when_mixed_ids(api_client, user, admin, sample_calculations):
    """
    Если передать id своих и чужих расчётов, обычный пользователь должен получить архив
    только со своими данными. Точное содержимое не проверяем, но файл должен создаться.
    """
    client = Client()
    client.force_login(user)
    url = "/api/calculations/export/"
    own_id = sample_calculations["user_calc"].id
    foreign_id = sample_calculations["admin_calc"].id

    response = client.post(url, {"ids": [own_id, foreign_id]})

    # Архив должен сформироваться, даже если часть id отфильтрована
    assert response.status_code == 200
    assert len(response.content) > 0



