import io
import decimal
import pandas as pd

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from trades.models import Item, Calculation, CalculationItem, PriceHistory, CustomUser

User = get_user_model()

# ===============================
# Тесты для представления item_list
# ===============================
class ItemListViewTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_item_list_get(self):
        url = reverse('item_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'trades/item_list.html')

    def test_add_item(self):
        url = reverse('item_list')
        post_data = {
            'add_item': '1',
            'name': 'Test Item',
            'price': '10.00'
        }
        response = self.client.post(url, post_data, follow=True)
        self.assertContains(response, "Товар успешно добавлен!")
        self.assertTrue(Item.objects.filter(name='Test Item').exists())

    def test_edit_item(self):
        item = Item.objects.create(name='Test Item', price=decimal.Decimal("10.00"))
        url = reverse('item_list')
        post_data = {
            'edit_item': str(item.id),
            f'name_{item.id}': 'Updated Item',
            f'price_{item.id}': '12.00'
        }
        response = self.client.post(url, post_data, follow=True)
        self.assertContains(response, "Товар успешно обновлён!")
        item.refresh_from_db()
        self.assertEqual(item.name, 'Updated Item')
        self.assertEqual(item.price, decimal.Decimal("12.00"))

    def test_delete_item(self):
        item = Item.objects.create(name='Test Item', price=decimal.Decimal("10.00"))
        url = reverse('item_list')
        post_data = {'delete_item': str(item.id)}
        response = self.client.post(url, post_data, follow=True)
        self.assertContains(response, "Товар успешно удалён!")
        self.assertFalse(Item.objects.filter(id=item.id).exists())

    def test_upload_file(self):
        df = pd.DataFrame({
            'Наименование комплектующей': ['Excel Item'],
            'Цена': [15.00]
        })
        buffer = io.BytesIO()
        df.to_excel(buffer, index=False)
        buffer.seek(0)
        uploaded_file = SimpleUploadedFile("test.xlsx", buffer.getvalue(), content_type="application/vnd.ms-excel")
        url = reverse('item_list')
        post_data = {'upload_file': '1'}
        response = self.client.post(url, {**post_data, 'file': uploaded_file}, follow=True)
        self.assertContains(response, "Товары загружены!")
        self.assertTrue(Item.objects.filter(name='Excel Item').exists())

# ===============================
# Тесты для представлений, связанных с расчётами
# ===============================
class CalculationsViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.item1 = Item.objects.create(name="Item1", price=decimal.Decimal("10.00"))
        self.item2 = Item.objects.create(name="Item2", price=decimal.Decimal("20.00"))

    def test_calculations_list_get(self):
        url = reverse('calculations_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'trades/calculations_list.html')

    def test_create_calculation(self):
        url = reverse('create_calculation')
        post_data = {
            'title': 'Calc Test',
            'markup': '10',
            'items': [str(self.item1.id), str(self.item2.id)],
            f'quantity_{self.item1.id}': '2',
            f'quantity_{self.item2.id}': '3'
        }
        response = self.client.post(url, post_data, follow=True)
        self.assertContains(response, "Расчёт успешно создан!")
        calc = Calculation.objects.get(title='Calc Test')
        self.assertEqual(calc.markup, decimal.Decimal("10"))
        self.assertEqual(calc.items.count(), 2)

    def test_calculation_detail_save(self):
        calc = Calculation.objects.create(title="Calc Detail", markup=decimal.Decimal("5"))
        calc_item = CalculationItem.objects.create(calculation=calc, item=self.item1, quantity=1)
        url = reverse('calculation_detail', kwargs={'pk': calc.pk})
        post_data = {
            'save_calculation': '1',
            f'quantity_{calc_item.id}': '5',
            'markup': '15'
        }
        response = self.client.post(url, post_data, follow=True)
        self.assertContains(response, "Расчёт успешно сохранён!")
        calc.refresh_from_db()
        calc_item.refresh_from_db()
        self.assertEqual(calc_item.quantity, 5)
        self.assertEqual(calc.markup, decimal.Decimal("15"))

# ===============================
# Тесты для представления истории цен
# ===============================
class PriceHistoryViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.item = Item.objects.create(name="History Item", price=decimal.Decimal("50.00"))
        PriceHistory.objects.create(item=self.item, old_price=decimal.Decimal("40.00"), new_price=decimal.Decimal("50.00"))

    def test_price_history_view(self):
        # Убедитесь, что в urls.py есть URL с именем 'price_history'
        url = reverse('price_history')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'trades/price_history.html')
        self.assertContains(response, "History Item")

# ===============================
# Тесты для управления пользователями (требуют аутентификации)
# ===============================
class UserManagementViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Создаем пользователей: admin и regular
        self.admin_user = CustomUser.objects.create_user(username="admin", email="admin@example.com", password="secret")
        self.regular_user = CustomUser.objects.create_user(username="user", email="user@example.com", password="secret")

    def login_admin(self):
        self.client.force_login(self.admin_user)

    def test_manage_users_view(self):
        self.login_admin()
        url = reverse('manage_users')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'trades/manage_users.html')
        self.assertContains(response, "admin")
        self.assertContains(response, "user")

    def test_create_user_get(self):
        self.login_admin()
        url = reverse('create_user')
        response = self.client.get(url)
        # Если тест все еще возвращает 302, проверьте настройки LOGIN_URL и URL-конфигурацию.
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'trades/create_user.html')

    def test_create_user_post(self):
        self.login_admin()
        url = reverse('create_user')
        post_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'strongpass123',
            'password2': 'strongpass123',
            'is_admin': False,
        }
        response = self.client.post(url, post_data, follow=True)
        # Если редирект приводит к 404, проверьте, что URL 'manage_users' корректно настроен.
        self.assertContains(response, "Пользователь успешно создан!")
        self.assertTrue(CustomUser.objects.filter(username='newuser').exists())

    def test_edit_user_view(self):
        self.login_admin()
        url = reverse('edit_user', kwargs={'user_id': self.regular_user.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'trades/edit_user.html')
        post_data = {
            'username': 'updateduser',
            'email': 'updated@example.com',
            'is_admin': self.regular_user.is_admin,
        }
        response = self.client.post(url, post_data, follow=True)
        self.assertContains(response, "Пользователь успешно обновлён!")
        self.regular_user.refresh_from_db()
        self.assertEqual(self.regular_user.username, 'updateduser')
        self.assertEqual(self.regular_user.email, 'updated@example.com')

    def test_delete_user_view(self):
        self.login_admin()
        url = reverse('delete_user', kwargs={'user_id': self.regular_user.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'trades/delete_user.html')
        response = self.client.post(url, follow=True)
        self.assertContains(response, "Пользователь успешно удалён!")
        self.assertFalse(CustomUser.objects.filter(pk=self.regular_user.pk).exists())
