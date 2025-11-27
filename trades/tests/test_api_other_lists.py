from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from trades.models import Item, PriceHistory, Calculation, CalculationItem


@pytest.fixture
def api_client():
  return APIClient()


@pytest.fixture
def admin(db):
  User = get_user_model()
  return User.objects.create_user(username="admin2", password="pass123", is_superuser=True, is_admin=True)


@pytest.mark.django_db
def test_price_history_list_for_admin(api_client, admin):
  """
  Базовая проверка: админ может получить список истории цен без ошибок.
  """
  user = admin
  api_client.force_authenticate(user=user)

  item = Item.objects.create(name="Товар для истории", price=Decimal("5.00"))
  PriceHistory.objects.create(item=item, old_price=Decimal("5.00"), new_price=Decimal("6.00"), changed_by=user)

  response = api_client.get("/api/price-history/")
  assert response.status_code == 200
  assert response.data["count"] >= 1


@pytest.mark.django_db
def test_snapshots_list_for_admin(api_client, admin):
  """
  Базовая проверка: админ может получить список снимков расчётов.
  """
  user = admin
  api_client.force_authenticate(user=user)

  # создаём простой расчёт и снимок через API
  item = Item.objects.create(name="Товар для снимка", price=Decimal("7.00"))
  calc = Calculation.objects.create(user=user, title="Расчёт для снимка", markup=Decimal("0"))
  CalculationItem.objects.create(calculation=calc, item=item, quantity=1)
  calc.refresh_totals()

  # создаём снимок через action save_snapshot
  response_snapshot = api_client.post(f"/api/calculations/{calc.id}/save_snapshot/")
  assert response_snapshot.status_code == 201

  response = api_client.get("/api/snapshots/")
  assert response.status_code == 200
  assert response.data["count"] >= 1


@pytest.mark.django_db
def test_users_list_requires_admin(api_client, admin):
  """
  Эндпоинт /api/users/ доступен только админу.
  """
  # неавторизованный – 401/403
  response_anon = api_client.get("/api/users/")
  assert response_anon.status_code in (401, 403)

  # обычный пользователь – PermissionDenied
  User = get_user_model()
  regular = User.objects.create_user(username="regular", password="pass123", is_admin=False)
  api_client.force_authenticate(user=regular)
  response_regular = api_client.get("/api/users/")
  assert response_regular.status_code in (403, 404)

  # админ – видит список
  api_client.force_authenticate(user=admin)
  response_admin = api_client.get("/api/users/")
  assert response_admin.status_code == 200


