from rest_framework import serializers
from .models import Item, Calculation, CalculationItem, CustomUser, PriceHistory, CalculationSnapshot, CalculationSnapshotItem

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'is_admin']

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['id', 'name', 'price']

class PriceHistorySerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source='item.name', read_only=True)
    changed_by_username = serializers.CharField(source='changed_by.username', read_only=True)
    
    class Meta:
        model = PriceHistory
        fields = ['id', 'item', 'item_name', 'old_price', 'new_price', 'changed_at', 'changed_by', 'changed_by_username']

class CalculationSnapshotItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CalculationSnapshotItem
        fields = ['id', 'item_name', 'item_price', 'quantity', 'total_price']

class CalculationSnapshotSerializer(serializers.ModelSerializer):
    items = CalculationSnapshotItemSerializer(many=True, read_only=True)
    calculation_title = serializers.CharField(source='calculation.title', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = CalculationSnapshot
        fields = [
            'id', 'calculation', 'calculation_title', 'frozen_total_price', 
            'frozen_total_price_with_markup', 'created_at', 'created_by', 
            'created_by_username', 'items'
        ]

class CalculationItemSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source='item.name', read_only=True)
    item_price = serializers.DecimalField(source='item.price', max_digits=10, decimal_places=2, read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = CalculationItem
        fields = ['id', 'item', 'item_name', 'item_price', 'quantity', 'total_price']

    def get_total_price(self, obj):
        return obj.total_price()

class CalculationSerializer(serializers.ModelSerializer):
    items = CalculationItemSerializer(many=True, read_only=True)
    items_count = serializers.SerializerMethodField()
    created_by = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Calculation
        fields = [
            'id', 'title', 'markup', 'created_at', 'created_by',
            'total_price', 'total_price_with_markup', 
            'items_count', 'items'
        ]
        read_only_fields = ['total_price', 'total_price_with_markup', 'created_at']

    def get_items_count(self, obj):
        return obj.items.count()

class CalculationCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания/обновления расчета.
    Принимает список items в формате: [{"item_id": 1, "quantity": 2}, ...]
    """
    items = serializers.ListField(child=serializers.DictField(), write_only=True)

    class Meta:
        model = Calculation
        fields = ['id', 'title', 'markup', 'items']

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        user = self.context['request'].user
        calculation = Calculation.objects.create(user=user, **validated_data)
        
        for item_data in items_data:
            CalculationItem.objects.create(
                calculation=calculation,
                item_id=item_data['item_id'],
                quantity=item_data.get('quantity', 1)
            )
        
        calculation.refresh_totals()
        return calculation

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)
        
        instance.title = validated_data.get('title', instance.title)
        instance.markup = validated_data.get('markup', instance.markup)
        instance.save()

        if items_data is not None:
            # Удаляем старые, создаем новые (простой способ обновления)
            # В "pro" версии лучше делать diff (обновлять существующие, удалять лишние),
            # но для начала так надежнее.
            instance.items.all().delete()
            for item_data in items_data:
                CalculationItem.objects.create(
                    calculation=instance,
                    item_id=item_data['item_id'],
                    quantity=item_data.get('quantity', 1)
                )
            instance.refresh_totals()
            
        return instance
