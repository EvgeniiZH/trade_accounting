from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models, transaction
from django.contrib.auth.models import User, AbstractUser, Permission, Group
from django.conf import settings  # Импорт для ссылки на модель пользователя
from django.db.models.signals import post_save
from django.dispatch import receiver


class Item(models.Model):
    name = models.CharField(max_length=255, unique=True)
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        db_index=True,
        validators=[MinValueValidator(Decimal('0.01'), message="Цена должна быть больше нуля")]
    )

    class Meta:
        indexes = [
            models.Index(fields=['name']),  # Для поиска по имени
        ]

    def __str__(self):
        return self.name


class Calculation(models.Model):
    # Привязка расчёта к пользователю
    # Поле user сделано опциональным: в тестах и некоторых сценариях расчёт может быть анонимным
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        default=None,
        db_index=True,
    )

    title = models.CharField(max_length=255)
    markup = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    # Поля для хранения итоговых сумм
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_price_with_markup = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        indexes = [
            models.Index(fields=['user', '-created_at']),  # Для фильтрации по пользователю и сортировки
            models.Index(fields=['-created_at']),  # Для общей сортировки по дате создания
        ]

    def total_price_without_markup_calc(self):
        """Вычисляет сумму без наценки по всем CalculationItem, связанным с этим расчетом."""
        return sum(item.total_price() for item in self.items.all())

    def calculate_total_price_with_markup(self):
        """Вычисляет сумму с учетом наценки."""
        total = self.total_price_without_markup_calc()
        return total + (total * self.markup / 100)

    def refresh_totals(self):
        """Пересчитывает итоговые суммы, блокируя запись, чтобы избежать гонок."""
        from .utils import calculate_total_price

        with transaction.atomic():
            locked = (
                Calculation.objects.select_for_update()
                .prefetch_related("items__item")
                .get(pk=self.pk)
            )
            total, total_with_markup = calculate_total_price(locked)
            locked.total_price = total
            locked.total_price_with_markup = total_with_markup
            locked.save(update_fields=["total_price", "total_price_with_markup"])

        self.total_price = total
        self.total_price_with_markup = total_with_markup
        return total, total_with_markup

    def __str__(self):
        return self.title


class CalculationItem(models.Model):
    calculation = models.ForeignKey(Calculation, related_name='items', on_delete=models.CASCADE, db_index=True)
    item = models.ForeignKey(Item, on_delete=models.CASCADE, db_index=True)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])

    def total_price(self):
        return self.item.price * self.quantity

    def __str__(self):
        return f"{self.item.name} x {self.quantity}"

    def save(self, *args, update_calculation=True, **kwargs):
        """Сохраняет позицию и при необходимости пересчитывает расчёт."""
        super().save(*args, **kwargs)

        if update_calculation and self.calculation_id:
            self.calculation.refresh_totals()

    def delete(self, *args, update_calculation=True, **kwargs):
        calculation = self.calculation if self.calculation_id else None
        super().delete(*args, **kwargs)
        if update_calculation and calculation:
            calculation.refresh_totals()




class PriceHistory(models.Model):
    item = models.ForeignKey('Item', on_delete=models.CASCADE, related_name="price_history", db_index=True)
    old_price = models.DecimalField(max_digits=10, decimal_places=2)
    new_price = models.DecimalField(max_digits=10, decimal_places=2)
    changed_at = models.DateTimeField(auto_now_add=True, db_index=True)
    # Новое поле для хранения пользователя, изменившего цену:
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Изменил",
        db_index=True,
    )

    class Meta:
        indexes = [
            models.Index(fields=['item', '-changed_at']),  # Для фильтрации по товару и сортировки по дате
            models.Index(fields=['-changed_at']),  # Для общей сортировки по дате изменения
        ]

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
    calculation = models.ForeignKey('Calculation', on_delete=models.CASCADE, related_name="snapshots", db_index=True)
    frozen_total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    frozen_total_price_with_markup = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Создал",
        db_index=True,
    )

    class Meta:
        indexes = [
            models.Index(fields=['calculation', '-created_at']),  # Для фильтрации по расчету и сортировки
            models.Index(fields=['-created_at']),  # Для общей сортировки по дате создания
        ]

    def __str__(self):
        return f"Snapshot of {self.calculation} at {self.created_at}"


class CalculationSnapshotItem(models.Model):
    snapshot = models.ForeignKey(CalculationSnapshot, on_delete=models.CASCADE, related_name="items", db_index=True)
    item_name = models.CharField(max_length=255)
    item_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.item_name} x {self.quantity} (Итого: {self.total_price})"


@receiver(post_save, sender=Item)
def refresh_calculation_totals_for_item(sender, instance, **kwargs):
    """После изменения товара пересчитываем связанные расчёты."""
    related_calculations = (
        Calculation.objects
        .filter(items__item=instance)
        .distinct()
    )

    for calculation in related_calculations:
        calculation.refresh_totals()

