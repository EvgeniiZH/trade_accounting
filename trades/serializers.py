from rest_framework import serializers
from .models import Item, Calculation, CalculationItem

# Сериализация товаров
class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = '__all__'

# Сериализация элементов расчёта
class CalculationItemSerializer(serializers.ModelSerializer):
    item_name = serializers.ReadOnlyField(source='item.name')  # Название товара
    item_price = serializers.ReadOnlyField(source='item.price')  # Цена товара
    total_price = serializers.SerializerMethodField()  # Вычисляемая итоговая стоимость

    class Meta:
        model = CalculationItem
        fields = ['id', 'item', 'item_name', 'item_price', 'quantity', 'total_price']

    def get_total_price(self, obj):
        return obj.total_price()  # Вызов метода модели

# Сериализация расчёта
class CalculationSerializer(serializers.ModelSerializer):
    items = CalculationItemSerializer(many=True, read_only=True)  # Список элементов расчёта

    class Meta:
        model = Calculation
        fields = ['id', 'title', 'created_at', 'items']
