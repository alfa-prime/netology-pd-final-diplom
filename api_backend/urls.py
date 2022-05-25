from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ShopViewSet, CategoryViewSet, ProductInfoViewSet, OrderViewSet, PartnerViewSet

router = DefaultRouter()
router.register('shops', ShopViewSet)
router.register('categories', CategoryViewSet)
router.register('product', ProductInfoViewSet)
router.register('orders', OrderViewSet, 'orders')
router.register('partner', PartnerViewSet, 'partner')

urlpatterns = [
    path('', include(router.urls)),
    # path('partner/update/', PartnerUpdate.as_view()),
]
