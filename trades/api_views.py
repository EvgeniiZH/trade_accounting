from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.core.exceptions import PermissionDenied
from .models import Item, Calculation, CalculationItem, PriceHistory, CalculationSnapshot, CustomUser
from .serializers import (
    ItemSerializer, 
    CalculationSerializer, 
    CalculationCreateUpdateSerializer,
    PriceHistorySerializer,
    CalculationSnapshotSerializer,
    UserSerializer
)

class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all().order_by('name')
    serializer_class = ItemSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'price']
    ordering = ['name']

class CalculationViewSet(viewsets.ModelViewSet):
    queryset = (
        Calculation.objects.all()
        .select_related('user')
        .prefetch_related('items__item')
        .order_by('-created_at')
    )
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title']
    ordering_fields = ['title', 'total_price', 'total_price_with_markup', 'created_at', 'markup']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CalculationCreateUpdateSerializer
        return CalculationSerializer

    def get_queryset(self):
        # Показывать только свои расчеты для обычных юзеров, все для админов
        user = self.request.user
        if user.is_superuser or user.is_admin:
            return super().get_queryset()
        return super().get_queryset().filter(user=user)
    
    @action(detail=True, methods=['post'])
    def copy(self, request, pk=None):
        """Копировать расчёт"""
        original = self.get_object()
        new_calculation = Calculation.objects.create(
            user=request.user,
            title=f"{original.title} (копия)",
            markup=original.markup
        )
        
        for item in original.items.all():
            CalculationItem.objects.create(
                calculation=new_calculation,
                item=item.item,
                quantity=item.quantity
            )
        
        new_calculation.refresh_totals()
        serializer = CalculationSerializer(new_calculation)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def save_snapshot(self, request, pk=None):
        """Сохранить снимок расчёта"""
        calculation = self.get_object()
        snapshot = CalculationSnapshot.objects.create(
            calculation=calculation,
            frozen_total_price=calculation.total_price,
            frozen_total_price_with_markup=calculation.total_price_with_markup,
            created_by=request.user
        )
        
        from .models import CalculationSnapshotItem
        snapshot_items = []
        for calc_item in calculation.items.all():
            snapshot_items.append(
                CalculationSnapshotItem(
                    snapshot=snapshot,
                    item_name=calc_item.item.name,
                    item_price=calc_item.item.price,
                    quantity=calc_item.quantity,
                    total_price=calc_item.total_price()
                )
            )
        if snapshot_items:
            CalculationSnapshotItem.objects.bulk_create(snapshot_items)
        
        serializer = CalculationSnapshotSerializer(snapshot)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class PriceHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PriceHistory.objects.all().select_related('item', 'changed_by').order_by('-changed_at')
    serializer_class = PriceHistorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['item__name']

class CalculationSnapshotViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CalculationSnapshot.objects.all().select_related('calculation', 'created_by').prefetch_related('items').order_by('-created_at')
    serializer_class = CalculationSnapshotSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['calculation__title']

class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all().order_by('username')
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Только админы могут видеть список пользователей
        if not (self.request.user.is_superuser or self.request.user.is_admin):
            raise PermissionDenied("Только администраторы имеют доступ")
        return super().get_queryset()
    
    def create(self, request, *args, **kwargs):
        if not (request.user.is_superuser or request.user.is_admin):
            raise PermissionDenied("Только администраторы могут создавать пользователей")
        return super().create(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        if not (request.user.is_superuser or request.user.is_admin):
            raise PermissionDenied("Только администраторы могут редактировать пользователей")
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        if not (request.user.is_superuser or request.user.is_admin):
            raise PermissionDenied("Только администраторы могут удалять пользователей")
        return super().destroy(request, *args, **kwargs)


