from django.contrib import admin
from .models import Item, Calculation, CalculationItem, UserSettings

# Регистрация моделей в админке
admin.site.register(Item)
admin.site.register(Calculation)
admin.site.register(CalculationItem)

@admin.register(UserSettings)
class UserSettingsAdmin(admin.ModelAdmin):
    list_display = ('user', 'decimal_places_price', 'decimal_places_percentage')