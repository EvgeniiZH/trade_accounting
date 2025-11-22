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
        self.user = User.objects.create_user(username='item-user', password='pass')
        self.client.force_login(self.user)

    def test_item_list_get(self):
        """
        Проверяем, что GET-запрос к странице товаров возвращает код 200.
        Если падает с NoReverseMatch, убедитесь, что в urls.py есть URL с именем 'item_list'
        и шаблон 'trades/item_list.html' существует.
        """
        url = reverse('item_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'trades/item_list.html')

    def test_add_item(self):
        """
        Тест добавления товара.
        Если возникает ошибка 404 или редирект (302), проверьте, что view корректно обрабатывает
        POST-параметр 'add_item'.
        """
        url = reverse('item_list')
        post_data = {
            'add_item': '1',
            'name': 'Test Item',
            'price': '10.5'
        }
        response = self.client.post(url, post_data, follow=True)
        self.assertContains(response, "Товар успешно добавлен!")
        self.assertEqual(Item.objects.filter(name='Test Item').count(), 1)

    def test_edit_item(self):
        """
        Тест редактирования товара.
        Обратите внимание: если сравнение цены дает '7.00' вместо '7.0',
        сравните объекты Decimal.
        """
        item = Item.objects.create(name='Original Item', price='5.0')
        url = reverse('item_list')
        post_data = {
            'edit_item': str(item.id),
            f'name_{item.id}': 'Edited Item',
            f'price_{item.id}': '7.0'
        }
        response = self.client.post(url, post_data, follow=True)
        self.assertContains(response, "Товар успешно обновлён!")
        item.refresh_from_db()
        self.assertEqual(item.name, 'Edited Item')
        self.assertEqual(item.price, decimal.Decimal('7.0'))

    def test_delete_item(self):
        """
        Тест удаления товара.
        Если view не находит нужный товар или происходит редирект, проверьте логику удаления.
        """
        item = Item.objects.create(name='To Delete', price='3.0')
        url = reverse('item_list')
        post_data = {
            'delete_item': str(item.id)
        }
        response = self.client.post(url, post_data, follow=True)
        self.assertContains(response, "Товар успешно удалён!")
        self.assertFalse(Item.objects.filter(id=item.id).exists())

    def test_upload_file(self):
        """
        Тест загрузки Excel-файла.
        Если появляется ошибка NoReverseMatch для 'price_history', это означает, что где-то в шаблоне
        вызывается reverse('price_history') – исправьте это или добавьте URL с таким именем.
        """
        df = pd.DataFrame({
            'Наименование комплектующей': ['Excel Item'],
            'Цена': [12.34]
        })
        buffer = io.BytesIO()
        df.to_excel(buffer, index=False)
        buffer.seek(0)
        upload_file = SimpleUploadedFile("test.xlsx", buffer.getvalue(), content_type="application/vnd.ms-excel")
        url = reverse('item_list')
        post_data = {'upload_file': '1'}
        response = self.client.post(url, {**post_data, 'file': upload_file}, follow=True)
        self.assertContains(response, "Товары загружены!")
        self.assertTrue(Item.objects.filter(name='Excel Item').exists())

# ===============================
# Тесты для представлений, связанных с расчётами
# ===============================
class CalculationsViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='calc-user', password='pass')
        self.client.force_login(self.user)
        self.item1 = Item.objects.create(name='Item1', price='10.0')
        self.item2 = Item.objects.create(name='Item2', price='20.0')

    def test_calculations_list_get(self):
        """
        Проверяем, что GET-запрос к списку расчётов возвращает страницу.
        Если падает, убедитесь, что в urls.py есть URL с именем 'calculations_list'
        и соответствующий шаблон.
        """
        url = reverse('calculations_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'trades/calculations_list.html')

    def test_create_calculation_post(self):
        """
        Тест создания нового расчёта.
        При сравнении наценки используем Decimal.
        """
        url = reverse('create_calculation')
        post_data = {
            'title': 'Test Calculation',
            'markup': '10',
            'items': [str(self.item1.id), str(self.item2.id)],
            f'quantity_{self.item1.id}': '2',
            f'quantity_{self.item2.id}': '3'
        }
        response = self.client.post(url, post_data, follow=True)
        self.assertContains(response, "Расчёт успешно создан!")
        calculation = Calculation.objects.get(title='Test Calculation')
        self.assertEqual(calculation.markup, decimal.Decimal('10'))
        self.assertEqual(calculation.items.count(), 2)

    def test_calculation_detail_save_calculation(self):
        """
        Тест обновления расчёта через детальную страницу.
        Если view вызывает reverse('price_history') внутри шаблона, а такого URL нет,
        это вызовет NoReverseMatch.
        """
        calculation = Calculation.objects.create(title='Calc Detail', markup=decimal.Decimal('5'), user=self.user)
        calc_item = CalculationItem.objects.create(calculation=calculation, item=self.item1, quantity=1)
        url = reverse('calculation_detail', kwargs={'pk': calculation.pk})
        post_data = {
            'save_calculation': '1',
            'items': [str(self.item1.id)],
            f'quantity_{calc_item.id}': '5',
            'markup': '15'
        }
        response = self.client.post(url, post_data, follow=True)
        self.assertContains(response, "Расчёт успешно сохранён!")
        calculation.refresh_from_db()
        calc_item.refresh_from_db()
        self.assertEqual(calc_item.quantity, 5)
        self.assertEqual(calculation.markup, decimal.Decimal('15'))

    def test_calculation_detail_remove_item(self):
        calculation = Calculation.objects.create(title='Calc Detail Remove', markup=decimal.Decimal('0'), user=self.user)
        calc_item_a = CalculationItem.objects.create(calculation=calculation, item=self.item1, quantity=1)
        calc_item_b = CalculationItem.objects.create(calculation=calculation, item=self.item2, quantity=2)
        url = reverse('calculation_detail', kwargs={'pk': calculation.pk})
        post_data = {
            'save_calculation': '1',
            'items': [str(self.item1.id)],
            f'quantity_{self.item1.id}': '3',
            f'quantity_{self.item2.id}': '1',
            'markup': '5',
        }
        response = self.client.post(url, post_data, follow=True)
        self.assertContains(response, "Расчёт успешно сохранён!")
        calculation.refresh_from_db()
        self.assertEqual(calculation.items.count(), 1)
        calc_item_a.refresh_from_db()
        self.assertEqual(calc_item_a.quantity, 3)
        self.assertFalse(CalculationItem.objects.filter(pk=calc_item_b.pk).exists())

# ===============================
# Тесты для представления истории цен
# ===============================
class PriceHistoryViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='history-user', password='pass')
        self.client.force_login(self.user)
        self.item = Item.objects.create(name='History Item', price='50.0')
        PriceHistory.objects.create(item=self.item, old_price='40.0', new_price='50.0')

    def test_price_history_view(self):
        """
        Тест для представления истории цен.
        Если ошибка NoReverseMatch возникает, значит в urls.py нет URL с именем 'price_history'.
        Проверьте, что в urls.py присутствует, например:
            path('price-history/', views.price_history_view, name='price_history')
        """
        url = reverse('price_history')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'trades/price_history.html')
        self.assertContains(response, 'History Item')

# ===============================
# Тесты для управления пользователями (views, требующих аутентификации)
# ===============================
class UserManagementViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = CustomUser.objects.create_user(
            username='admin', email='admin@example.com', password='secret'
        )
        self.admin_user.is_admin = True
        self.admin_user.save(update_fields=['is_admin'])
        self.user = CustomUser.objects.create_user(
            username='user', email='user@example.com', password='secret'
        )

    def login_admin(self):
        self.client.force_login(self.admin_user)

    def test_manage_users_forbidden_for_non_admin(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('manage_users'))
        self.assertEqual(response.status_code, 403)

    def test_create_user_forbidden_for_non_admin(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('create_user'))
        self.assertEqual(response.status_code, 403)

    def test_edit_user_forbidden_for_non_admin(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('edit_user', kwargs={'user_id': self.admin_user.pk}))
        self.assertEqual(response.status_code, 403)

    def test_delete_user_forbidden_for_non_admin(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('delete_user', kwargs={'user_id': self.admin_user.pk}))
        self.assertEqual(response.status_code, 403)

    def test_manage_users_view(self):
        self.login_admin()
        response = self.client.get(reverse('manage_users'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'trades/manage_users.html')
        self.assertContains(response, 'admin')
        self.assertContains(response, 'user')

    def test_create_user_view_get(self):
        self.login_admin()
        response = self.client.get(reverse('create_user'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'trades/create_user.html')

    def test_create_user_view_post(self):
        self.login_admin()
        url = reverse('create_user')
        post_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'strongpassword123',
            'password2': 'strongpassword123',
            'is_admin': False,
        }
        response = self.client.post(url, post_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(CustomUser.objects.filter(username='newuser').exists())

    def test_edit_user_view(self):
        self.login_admin()
        url = reverse('edit_user', kwargs={'user_id': self.user.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'trades/edit_user.html')
        post_data = {
            'username': 'updateduser',
            'email': 'updated@example.com',
            'is_admin': self.user.is_admin,
        }
        response = self.client.post(url, post_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'updateduser')
        self.assertEqual(self.user.email, 'updated@example.com')

    def test_delete_user_view(self):
        self.login_admin()
        url = reverse('delete_user', kwargs={'user_id': self.user.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'trades/delete_user.html')
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(CustomUser.objects.filter(pk=self.user.pk).exists())




