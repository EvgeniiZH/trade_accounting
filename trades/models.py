from django.db import models
from django.contrib.auth.models import User, AbstractUser, Permission, Group


class Item(models.Model):
    name = models.CharField(max_length=255, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name


class Calculation(models.Model):
    title = models.CharField(max_length=255)
    markup = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def total_price_without_markup(self):
        return sum(item.total_price() for item in self.items.all())

    def total_price_with_markup(self):
        total = self.total_price_without_markup()
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




class PriceHistory(models.Model):
    item = models.ForeignKey('Item', on_delete=models.CASCADE, related_name="price_history")
    old_price = models.DecimalField(max_digits=10, decimal_places=2)
    new_price = models.DecimalField(max_digits=10, decimal_places=2)
    changed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.item.name} | {self.old_price} → {self.new_price} ({self.changed_at})"


class CustomUser(AbstractUser):
    """Кастомная модель пользователя с исправленными связями"""
    is_admin = models.BooleanField(default=False, verbose_name="Администратор")

    groups = models.ManyToManyField(Group, related_name="customuser_set", blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name="customuser_permissions_set", blank=True)

    def __str__(self):
        return self.username