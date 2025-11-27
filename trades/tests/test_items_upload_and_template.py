import io
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client
from rest_framework.test import APIClient
import pandas as pd

from trades.models import Item


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def admin(db):
    User = get_user_model()
    return User.objects.create_user(username="upload_admin", password="pass123", is_superuser=True, is_admin=True)


@pytest.mark.django_db
def test_download_import_template(api_client, admin):
    api_client.force_authenticate(user=admin)
    response = api_client.get("/api/download-template/")

    assert response.status_code == 200
    assert "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" in response["Content-Type"]
    assert len(response.content) > 0

    # Проверяем, что в шаблоне есть нужные колонки
    excel_bytes = io.BytesIO(response.content)
    df = pd.read_excel(excel_bytes)
    assert list(df.columns) == ["Наименование комплектующей", "Цена"]


@pytest.mark.django_db
def test_upload_items_api_success(api_client, admin, tmp_path):
    client = Client()
    client.force_login(admin)

    # Готовим небольшой Excel-файл в памяти
    df = pd.DataFrame(
        [
            {"Наименование комплектующей": "Товар 1", "Цена": 10.5},
            {"Наименование комплектующей": "Товар 2", "Цена": 20},
        ]
    )
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False)
    buffer.seek(0)

    uploaded = SimpleUploadedFile("items.xlsx", buffer.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    response = client.post("/api/upload-items/", {"file": uploaded}, format="multipart")

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["created"] == 2
    assert Item.objects.filter(name="Товар 1").exists()
    assert Item.objects.filter(name="Товар 2").exists()


@pytest.mark.django_db
def test_upload_items_api_missing_file(api_client, admin):
    """
    Если файл не передан, должен вернуться 400.
    """
    client = Client()
    client.force_login(admin)
    response = client.post("/api/upload-items/", {}, format="multipart")
    assert response.status_code == 400
    assert "No file" in response.json().get("error", "") or "file" in response.json().get("error", "").lower()


@pytest.mark.django_db
def test_upload_items_api_wrong_method(api_client, admin):
    """
    Любой метод кроме POST должен вернуть 405.
    """
    client = Client()
    client.force_login(admin)
    response = client.get("/api/upload-items/")
    assert response.status_code == 405


