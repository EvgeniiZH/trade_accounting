from django.contrib import admin
from .models import Item, Calculation, CalculationItem

# Регистрация моделей в админке
admin.site.register(Item)
admin.site.register(Calculation)
admin.site.register(CalculationItem)

class UserSettingsAdmin(admin.ModelAdmin):
    list_display = ('decimal_places_price', 'decimal_places_percentage', 'price_step')
    list_display_links = ('decimal_places_price',)  # Делаем первое поле ссылкой
    list_editable = ('decimal_places_percentage', 'price_step')  # Остальные поля остаются редактируемыми

