from decimal import Decimal
from django.test import TestCase
from django.db import transaction
from django.contrib.auth import get_user_model
from .models import Item, Calculation, CalculationItem

User = get_user_model()

class CalculationTests(TestCase):
    def setUp(self):
        # Создаем тестового пользователя
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )
        
        # Создаем тестовые товары
        self.item1 = Item.objects.create(
            name='Test Item 1',
            price=Decimal('100.00')
        )
        self.item2 = Item.objects.create(
            name='Test Item 2',
            price=Decimal('200.00')
        )

    def test_calculation_total_price(self):
        """Проверка корректности расчета общей стоимости"""
        # Создаем расчет
        calc = Calculation.objects.create(
            user=self.user,
            title='Test Calculation',
            markup=Decimal('10.00')  # 10% наценка
        )

        # Добавляем товары
        CalculationItem.objects.create(
            calculation=calc,
            item=self.item1,
            quantity=2
        )
        CalculationItem.objects.create(
            calculation=calc,
            item=self.item2,
            quantity=1
        )

        # Проверяем расчеты
        expected_total = Decimal('400.00')  # (100 * 2) + (200 * 1)
        expected_total_with_markup = Decimal('440.00')  # 400 + (400 * 0.10)

        # Обновляем расчет из БД
        calc.refresh_from_db()
        
        self.assertEqual(calc.total_price, expected_total)
        self.assertEqual(calc.total_price_with_markup, expected_total_with_markup)

    def test_bulk_create_items(self):
        """Проверка корректности работы bulk_create"""
        calc = Calculation.objects.create(
            user=self.user,
            title='Bulk Test',
            markup=Decimal('10.00')
        )

        # Создаем несколько товаров через bulk_create
        items_to_create = [
            CalculationItem(calculation=calc, item=self.item1, quantity=1),
            CalculationItem(calculation=calc, item=self.item2, quantity=2)
        ]
        
        with transaction.atomic():
            CalculationItem.objects.bulk_create(items_to_create)
            # После bulk_create нужно обновить итоги вручную
            total = calc.total_price_without_markup_calc()
            calc.total_price = total
            calc.total_price_with_markup = total * (1 + calc.markup / 100)
            calc.save()

        # Обновляем расчет из БД
        calc.refresh_from_db()

        expected_total = Decimal('500.00')  # (100 * 1) + (200 * 2)
        expected_total_with_markup = Decimal('550.00')  # 500 + (500 * 0.10)

        self.assertEqual(calc.total_price, expected_total)
        self.assertEqual(calc.total_price_with_markup, expected_total_with_markup)

    def test_concurrent_updates(self):
        """Тест на конкурентные обновления (имитация)"""
        calc = Calculation.objects.create(
            user=self.user,
            title='Concurrent Test',
            markup=Decimal('10.00')
        )

        # Создаем первый товар
        item1 = CalculationItem.objects.create(
            calculation=calc,
            item=self.item1,
            quantity=1
        )

        # Имитируем конкурентное обновление
        with transaction.atomic():
            # Получаем свежую версию из БД
            calc_concurrent = Calculation.objects.select_for_update().get(id=calc.id)
            
            # Добавляем второй товар
            CalculationItem.objects.create(
                calculation=calc_concurrent,
                item=self.item2,
                quantity=1
            )

        # Проверяем итоговые суммы
        calc.refresh_from_db()
        expected_total = Decimal('300.00')  # 100 + 200
        expected_total_with_markup = Decimal('330.00')  # 300 + (300 * 0.10)

        self.assertEqual(calc.total_price, expected_total)
        self.assertEqual(calc.total_price_with_markup, expected_total_with_markup)

    def test_validation(self):
        """Проверка валидации цен и количества"""
        # Проверяем, что нельзя создать товар с отрицательной ценой
        with self.assertRaises(Exception):
            Item.objects.create(
                name='Invalid Item',
                price=Decimal('-100.00')
            )

        # Проверяем, что нельзя создать CalculationItem с нулевым количеством
        calc = Calculation.objects.create(
            user=self.user,
            title='Validation Test'
        )
        
        with self.assertRaises(Exception):
            CalculationItem.objects.create(
                calculation=calc,
                item=self.item1,
                quantity=0
            )