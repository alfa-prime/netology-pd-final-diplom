from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import PartnerUpdate, ShopViewSet

router = DefaultRouter()
router.register('shops', ShopViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('partner/update/', PartnerUpdate.as_view()),
]
