from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from trades.models import Item, Calculation, CalculationItem


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    User = get_user_model()
    return User.objects.create_user(username="calc_user", password="pass123")


@pytest.mark.django_db
def test_create_calculation_via_api(api_client, user):
    """
    Создание расчёта через DRF CalculationViewSet (POST /api/calculations/).
    Проверяем пересчёт total_price и total_price_with_markup.
    """
    api_client.force_authenticate(user=user)

    item1 = Item.objects.create(name="Тестовый товар 1", price=Decimal("10.00"))
    item2 = Item.objects.create(name="Тестовый товар 2", price=Decimal("20.00"))

    payload = {
        "title": "API расчёт",
        "markup": "10.0",
        "items": [
            {"item_id": item1.id, "quantity": 2},
            {"item_id": item2.id, "quantity": 1},
        ],
    }

    response = api_client.post("/api/calculations/", payload, format="json")
    assert response.status_code == 201
    data = response.data

    calc = Calculation.objects.get(id=data["id"])
    # total без наценки: 2*10 + 1*20 = 40
    assert calc.total_price == Decimal("40.00")
    # total с наценкой 10% = 44.00
    assert calc.total_price_with_markup == Decimal("44.00")


@pytest.mark.django_db
def test_update_calculation_via_api_recalculates_totals(api_client, user):
    """
    Обновление расчёта через PUT /api/calculations/{id}/ должно пересчитывать суммы.
    """
    api_client.force_authenticate(user=user)

    item = Item.objects.create(name="Тестовый товар", price=Decimal("15.00"))
    calc = Calculation.objects.create(user=user, title="Старый расчёт", markup=Decimal("0"))
    CalculationItem.objects.create(calculation=calc, item=item, quantity=1)
    calc.refresh_totals()

    payload = {
        "title": "Обновлённый расчёт",
        "markup": "20.0",
        "items": [
            {"item_id": item.id, "quantity": 3},
        ],
    }

    response = api_client.put(f"/api/calculations/{calc.id}/", payload, format="json")
    assert response.status_code == 200

    calc.refresh_from_db()
    # total без наценки: 3 * 15 = 45
    assert calc.total_price == Decimal("45.00")
    # total с наценкой 20% = 54.00
    assert calc.total_price_with_markup == Decimal("54.00")


