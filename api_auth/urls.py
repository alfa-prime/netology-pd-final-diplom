from django.urls import path, include

from .views import request_user_activation


urlpatterns = [
    path('', include('djoser.urls')),
    path('', include('djoser.urls.authtoken')),
    path('user/activate/<str:uid>/<str:token>', request_user_activation),
]
