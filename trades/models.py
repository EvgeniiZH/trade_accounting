from django.db import models
from django.contrib.auth.models import User

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


class UserSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    decimal_places_price = models.PositiveIntegerField(default=2)
    decimal_places_percentage = models.PositiveIntegerField(default=2)
    price_step = models.DecimalField(max_digits=5, decimal_places=2, default=0.01)  # Новый атрибут

    def __str__(self):
        return f"Настройки пользователя {self.user.username}"

