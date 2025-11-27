import random
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model

from trades.models import (
    Item,
    Calculation,
    CalculationItem,
    PriceHistory,
    CalculationSnapshot,
    CalculationSnapshotItem,
)


class Command(BaseCommand):
    help = "Создаёт тестовые данные: пользователей, товары, расчёты, историю цен и архив"

    def handle(self, *args, **options):
        User = get_user_model()

        self.stdout.write(self.style.MIGRATE_HEADING("===> Создание пользователей"))

        admin, created = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@example.com",
                "is_superuser": True,
                "is_staff": True,
                "is_admin": True,
            },
        )
        if created:
            admin.set_password("admin123")
            admin.save()
            self.stdout.write(self.style.SUCCESS("Создан админ-пользователь admin / admin123"))
        else:
            self.stdout.write("Админ-пользователь уже существует")

        user1, _ = User.objects.get_or_create(
            username="manager1",
            defaults={"email": "manager1@example.com", "is_staff": False, "is_admin": False},
        )
        user2, _ = User.objects.get_or_create(
            username="manager2",
            defaults={"email": "manager2@example.com", "is_staff": False, "is_admin": False},
        )

        self.stdout.write(self.style.MIGRATE_HEADING("===> Создание товаров"))

        item_names = [
            "Кабель витая пара UTP",
            "Розетка двойная",
            "Выключатель проходной",
            "Автоматический выключатель 16A",
            "Автоматический выключатель 25A",
            "Светильник светодиодный 12W",
            "Светильник светодиодный 24W",
            "Труба гофрированная 16мм",
            "Труба гофрированная 20мм",
            "Коробка распределительная",
            "Клеммник WAGO 3-проводный",
            "Клеммник WAGO 5-проводный",
            "Кабель силовой 3x2.5",
            "Кабель силовой 3x1.5",
            "Гофра металлизированная 25мм",
            "Лампа светодиодная 10W",
            "Лампа светодиодная 7W",
            "Щиток распределительный 12 модулей",
            "Щиток распределительный 24 модуля",
            "УЗО 30mA",
        ]

        items = []
        for name in item_names:
            price = Decimal(random.randrange(50, 5000)) / 100  # 0.50 - 50.00
            item, _ = Item.objects.get_or_create(
                name=name,
                defaults={"price": price},
            )
            items.append(item)
        self.stdout.write(self.style.SUCCESS(f"Всего товаров: {Item.objects.count()}"))

        self.stdout.write(self.style.MIGRATE_HEADING("===> Создание истории цен"))

        for item in random.sample(items, min(8, len(items))):
            old_price = item.price
            new_price = (old_price * Decimal("1.10")).quantize(Decimal("0.01"))
            PriceHistory.objects.get_or_create(
                item=item,
                old_price=old_price,
                new_price=new_price,
                changed_by=admin,
            )
            item.price = new_price
            item.save()

        self.stdout.write(self.style.SUCCESS(f"Всего записей истории цен: {PriceHistory.objects.count()}"))

        self.stdout.write(self.style.MIGRATE_HEADING("===> Создание расчётов"))

        # Удалять старое не будем, чтобы можно было вызывать несколько раз
        users_for_calcs = [admin, user1, user2]
        for user in users_for_calcs:
            for i in range(3):
                calc = Calculation.objects.create(
                    user=user,
                    title=f"Тестовый расчёт {user.username} #{i + 1}",
                    markup=Decimal(random.choice([0, 10, 15, 20])),
                )

                # Добавим от 3 до 7 позиций
                for item in random.sample(items, random.randint(3, 7)):
                    qty = random.randint(1, 10)
                    CalculationItem.objects.create(
                        calculation=calc,
                        item=item,
                        quantity=qty,
                    )

                calc.refresh_totals()

        self.stdout.write(self.style.SUCCESS(f"Всего расчётов: {Calculation.objects.count()}"))

        self.stdout.write(self.style.MIGRATE_HEADING("===> Создание снимков (архив)"))

        # Для каждого второго расчёта создадим snapshot
        for calc in Calculation.objects.all()[::2]:
            snapshot = CalculationSnapshot.objects.create(
                calculation=calc,
                frozen_total_price=calc.total_price,
                frozen_total_price_with_markup=calc.total_price_with_markup,
                created_by=calc.user,
            )

            snapshot_items = []
            for ci in calc.items.all():
                snapshot_items.append(
                    CalculationSnapshotItem(
                        snapshot=snapshot,
                        item_name=ci.item.name,
                        item_price=ci.item.price,
                        quantity=ci.quantity,
                        total_price=ci.total_price(),
                    )
                )
            CalculationSnapshotItem.objects.bulk_create(snapshot_items)

        self.stdout.write(self.style.SUCCESS(f"Всего снимков: {CalculationSnapshot.objects.count()}"))
        self.stdout.write(self.style.SUCCESS("Готово! Тестовые данные созданы."))



