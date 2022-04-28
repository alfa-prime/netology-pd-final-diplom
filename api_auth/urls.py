from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import request_user_activation, ContactViewSet

router = DefaultRouter()
router.register('contact', ContactViewSet, basename='contacts')


urlpatterns = [
    path('', include('djoser.urls')),
    path('', include('djoser.urls.authtoken')),
    path('user/activate/<str:uid>/<str:token>', request_user_activation),
    path('user/', include(router.urls))
]
