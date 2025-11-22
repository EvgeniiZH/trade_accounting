#!/usr/bin/env python
"""
Скрипт для импорта данных из старой базы данных в новую
Использование: python scripts/import_old_db.py
"""
import os
import django
import sys

# Настройка Django окружения
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trade_accounting.settings.local')
django.setup()

from django.core.management import call_command
from django.db import connection
from trades.models import CustomUser, Item, Calculation, CalculationItem, PriceHistory, CalculationSnapshot, CalculationSnapshotItem

def import_from_old_db():
    """Импорт данных из старой базы через прямое подключение"""
    # Параметры старой базы (можно взять из переменных окружения)
    old_db_config = {
        'NAME': 'django_project_db',
        'USER': 'django',
        'PASSWORD': 'me4ut9oodi3W',
        'HOST': 'trade_accounting-db-1',  # Имя контейнера старой БД
        'PORT': '5432',
    }
    
    print("Подключение к старой базе данных...")
    try:
        # Используем прямое подключение к PostgreSQL
        import psycopg2
        old_conn = psycopg2.connect(**old_db_config)
        old_cursor = old_conn.cursor()
        
        print("✅ Подключение установлено")
        
        # Импорт пользователей
        old_cursor.execute("SELECT id, username, email, password, is_staff, is_superuser, is_active, date_joined, is_admin FROM trades_customuser")
        users_data = old_cursor.fetchall()
        print(f"Найдено пользователей: {len(users_data)}")
        
        for user_row in users_data:
            user_id, username, email, password, is_staff, is_superuser, is_active, date_joined, is_admin = user_row
            if not CustomUser.objects.filter(id=user_id).exists():
                user = CustomUser.objects.create(
                    id=user_id,
                    username=username,
                    email=email or '',
                    password=password,
                    is_staff=is_staff,
                    is_superuser=is_superuser,
                    is_active=is_active,
                    date_joined=date_joined,
                    is_admin=is_admin or False
                )
                print(f"  ✓ Импортирован пользователь: {username}")
        
        # Импорт товаров
        old_cursor.execute("SELECT id, name, price FROM trades_item")
        items_data = old_cursor.fetchall()
        print(f"Найдено товаров: {len(items_data)}")
        
        for item_row in items_data:
            item_id, name, price = item_row
            if not Item.objects.filter(id=item_id).exists():
                Item.objects.create(id=item_id, name=name, price=price)
                print(f"  ✓ Импортирован товар: {name}")
        
        # Импорт расчётов
        old_cursor.execute("SELECT id, user_id, title, markup, created_at, total_price, total_price_with_markup FROM trades_calculation")
        calculations_data = old_cursor.fetchall()
        print(f"Найдено расчётов: {len(calculations_data)}")
        
        for calc_row in calculations_data:
            calc_id, user_id, title, markup, created_at, total_price, total_price_with_markup = calc_row
            if not Calculation.objects.filter(id=calc_id).exists():
                user = CustomUser.objects.get(id=user_id) if user_id else None
                Calculation.objects.create(
                    id=calc_id,
                    user=user,
                    title=title,
                    markup=markup,
                    created_at=created_at,
                    total_price=total_price,
                    total_price_with_markup=total_price_with_markup
                )
                print(f"  ✓ Импортирован расчёт: {title}")
        
        # Импорт позиций расчётов
        old_cursor.execute("SELECT id, calculation_id, item_id, quantity FROM trades_calculationitem")
        calc_items_data = old_cursor.fetchall()
        print(f"Найдено позиций расчётов: {len(calc_items_data)}")
        
        for ci_row in calc_items_data:
            ci_id, calc_id, item_id, quantity = ci_row
            if not CalculationItem.objects.filter(id=ci_id).exists():
                calculation = Calculation.objects.get(id=calc_id)
                item = Item.objects.get(id=item_id)
                CalculationItem.objects.create(
                    id=ci_id,
                    calculation=calculation,
                    item=item,
                    quantity=quantity
                )
        
        old_cursor.close()
        old_conn.close()
        
        print("\n✅ Импорт завершён успешно!")
        
    except Exception as e:
        print(f"❌ Ошибка при импорте: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    import_from_old_db()

