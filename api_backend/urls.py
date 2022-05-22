from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import PartnerUpdate, ShopViewSet, CategoryViewSet, ProductInfoViewSet

router = DefaultRouter()
router.register('shops', ShopViewSet)
router.register('categories', CategoryViewSet)
router.register('product', ProductInfoViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('partner/update/', PartnerUpdate.as_view()),
]
