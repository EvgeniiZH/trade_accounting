from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.contrib.auth.models import User, AbstractUser, Permission, Group
from django.conf import settings  # Импорт для ссылки на модель пользователя


class Item(models.Model):
    name = models.CharField(max_length=255, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name


class Calculation(models.Model):
    # Привязка расчёта к пользователю
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=False,
        blank=False
    )

    title = models.CharField(max_length=255)
    markup = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    # Поля для хранения итоговых сумм
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_price_with_markup = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def total_price_without_markup_calc(self):
        """Вычисляет сумму без наценки по всем CalculationItem, связанным с этим расчетом."""
        return sum(item.total_price() for item in self.items.all())

    def calculate_total_price_with_markup(self):
        """Вычисляет сумму с учетом наценки."""
        total = self.total_price_without_markup_calc()
        return total + (total * self.markup / 100)

    def __str__(self):
        return self.title


class CalculationItem(models.Model):
    calculation = models.ForeignKey(Calculation, related_name='items', on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def total_price(self):
        return self.item.price * self.quantity

    def __str__(self):
        return f"{self.item.name} x {self.quantity}"

    def save(self, *args, update_calculation=True, **kwargs):
        """
        Сохраняет элемент расчета и опционально обновляет итоговые суммы расчета.
        
        :param update_calculation: если True, обновит итоговые суммы в расчете
        """
        super().save(*args, **kwargs)
        
        if update_calculation:
            from django.db import transaction
            # Получаем свежую версию расчета из БД и блокируем для обновления
            with transaction.atomic():
                calculation = Calculation.objects.select_for_update().get(pk=self.calculation_id)
                calculation.total_price = calculation.total_price_without_markup_calc()
                calculation.total_price_with_markup = calculation.calculate_total_price_with_markup()
                calculation.save()


class PriceHistory(models.Model):
    item = models.ForeignKey('Item', on_delete=models.CASCADE, related_name="price_history")
    old_price = models.DecimalField(max_digits=10, decimal_places=2)
    new_price = models.DecimalField(max_digits=10, decimal_places=2)
    changed_at = models.DateTimeField(auto_now_add=True)
    # Новое поле для хранения пользователя, изменившего цену:
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Изменил"
    )

    def __str__(self):
        return f"{self.item.name} | {self.old_price} → {self.new_price} ({self.changed_at})"


class CustomUser(AbstractUser):
    """Кастомная модель пользователя с исправленными связями"""
    is_admin = models.BooleanField(default=False, verbose_name="Администратор")

    groups = models.ManyToManyField(Group, related_name="customuser_set", blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name="customuser_permissions_set", blank=True)

    def __str__(self):
        return self.username


class CalculationSnapshot(models.Model):
    calculation = models.ForeignKey('Calculation', on_delete=models.CASCADE, related_name="snapshots")
    frozen_total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    frozen_total_price_with_markup = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Создал"
    )

    def __str__(self):
        return f"Snapshot of {self.calculation} at {self.created_at}"


class CalculationSnapshotItem(models.Model):
    snapshot = models.ForeignKey(CalculationSnapshot, on_delete=models.CASCADE, related_name="items")
    item_name = models.CharField(max_length=255)
    item_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.item_name} x {self.quantity} (Итого: {self.total_price})"

