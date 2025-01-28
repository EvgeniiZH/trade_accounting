from rest_framework import serializers
from .models import Item, Calculation, CalculationItem

# Сериализация товаров
class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = '__all__'


# Сериализация элементов расчета
class CalculationItemSerializer(serializers.ModelSerializer):
    item_name = serializers.ReadOnlyField(source='item.name')  # Название товара
    item_price = serializers.ReadOnlyField(source='item.price')  # Цена товара

    class Meta:
        model = CalculationItem
        fields = ['id', 'item', 'item_name', 'item_price', 'quantity', 'total_price']


# Сериализация расчета
class CalculationSerializer(serializers.ModelSerializer):
    items = CalculationItemSerializer(many=True, read_only=True)  # Список элементов расчета

    class Meta:
        model = Calculation
        fields = ['id', 'title', 'created_at', 'items']
