from django.urls import path, include
from rest_framework.routers import DefaultRouter
from trades.api_views import (
    ItemViewSet, CalculationViewSet, PriceHistoryViewSet,
    CalculationSnapshotViewSet, UserViewSet
)
from trades import views

router = DefaultRouter()
router.register(r'items', ItemViewSet)
router.register(r'calculations', CalculationViewSet)
router.register(r'price-history', PriceHistoryViewSet, basename='pricehistory')
router.register(r'snapshots', CalculationSnapshotViewSet, basename='snapshot')
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    # ВАЖНО: путь экспорта должен идти ДО include(router.urls), иначе его перехватит роутер
    path('calculations/export/', views.export_calculations_excel_api, name='export_calculations_excel_api'),
    path('', include(router.urls)),
    path('upload-items/', views.upload_items_api, name='upload_items_api'),
    path('download-template/', views.download_import_template, name='download_template'),
]


