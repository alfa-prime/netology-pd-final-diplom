from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ShopViewSet, CategoryViewSet, ProductInfoViewSet, OrderViewSet, PartnerViewSet, BasketViewSet

router = DefaultRouter()
router.register('shops', ShopViewSet)
router.register('categories', CategoryViewSet)
router.register('product', ProductInfoViewSet)
router.register('partner', PartnerViewSet, 'partner')
router.register('basket', BasketViewSet, 'basket')
router.register('orders', OrderViewSet, 'orders')

urlpatterns = [
    path('', include(router.urls)),
]
