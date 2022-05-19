from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import PartnerUpdate, ShopViewSet


urlpatterns = [
    path('partner/update/', PartnerUpdate.as_view()),
    path('shops/', ShopViewSet.as_view({'get': 'list'}))
]
