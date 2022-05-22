from django.core.validators import URLValidator
from django.http import JsonResponse
from rest_framework import viewsets

from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView

import requests
from yaml import load as yaml_load, SafeLoader

from api_backend.mixins import ListRetrieveSerializersMixin
from api_backend.models import Shop, Category
from api_backend.serializers import ShopDetailSerializer, ShopsListSerializer, CategoryListSerializer, \
    CategoryDetailSerializer
from api_backend.services import partner_update


class PartnerUpdate(APIView):
    """
    Updating partner price list from the specified url
    """
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        if request.user.type != 'shop':
            return JsonResponse({'Status': False, 'Error': 'Only for shops'}, status=403)

        url = request.data.get('url')

        if url:
            validate_url = URLValidator()
            try:
                validate_url(url)
            except ValidationError as e:
                return JsonResponse({'Status': False, 'Error': str(e)})
            else:
                stream = requests.get(url).content
                data = yaml_load(stream, Loader=SafeLoader)
                user_id = request.user.id
                partner_update(user_id=user_id, data=data)
                return JsonResponse({'Status': True, 'Message': 'Price list successfully update'})

        return JsonResponse({'Status': False, 'Errors': 'All necessary arguments are not specified'})


class ShopViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Shops list
    """
    queryset = Shop.objects.all()
    filterset_fields = ('state',)
    ordering_fields = ('name', 'id',)
    search_fields = ('name',)
    ordering = ('name',)

    serializer_classes = {
        'list': ShopsListSerializer,
        'retrieve': ShopDetailSerializer,
    }
    default_serializer_class = ShopsListSerializer

    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.default_serializer_class)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Category list
    """
    queryset = Category.objects.all()
    serializer_list = CategoryListSerializer
    serializer_detail = CategoryDetailSerializer
    filterset_fields = ('name',)
    ordering_fields = ('name', 'id',)
    search_fields = ('name',)
    ordering = ('name',)

    serializer_classes = {
        'list': CategoryListSerializer,
        'retrieve': CategoryDetailSerializer,
    }
    default_serializer_class = CategoryListSerializer

    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.default_serializer_class)
