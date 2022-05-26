from django.db.models import Q, Sum, F, DecimalField
from django.http import JsonResponse
from rest_framework import viewsets
from rest_framework.decorators import action
from django.core.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework import status as http_status
from rest_framework.response import Response

from api_backend.models import Shop, Category, ProductInfo, Order
from api_backend.serializers import ShopDetailSerializer, ShopSerializer, CategorySerializer, \
    CategoryDetailSerializer, ProductInfoSerializer, OrderSerializer, StateSerializer
from api_backend.services import upload_partner_data, validate_url


class PartnerViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=('get', 'put'), url_name='state', url_path='state')
    def state(self, request, *args, **kwargs):
        """
        Change shop orders receipt status (on/off)
        """

        if request.method == 'GET':
            url = validate_url(request.data)
            shop = Shop.objects.filter(url=url).first()

            if shop:
                return JsonResponse({'state': shop.state}, status=http_status.HTTP_200_OK)
            else:
                return JsonResponse({'error': 'shop not found'}, status=http_status.HTTP_404_NOT_FOUND)
        else:
            serializer = StateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            shop = Shop.objects.filter(user_id=request.user.id).first()

            state = serializer.validated_data.get('state')
            shop.state = True if state == 'on' else False
            shop.save()

            return JsonResponse({'state': shop.state}, status=http_status.HTTP_200_OK)

    @action(detail=False, methods=('post', ), url_name='update', url_path='update')
    def update_price_list(self, request, *args, **kwargs):
        """
        Update partner price list
        """

        if request.user.type != 'shop':
            raise ValidationError({'error': 'Only for shops'})

        url = validate_url(request.data)
        upload_partner_data(url, None, request.user.id)

        return JsonResponse({'success': 'Price list successfully update'}, status=http_status.HTTP_200_OK)

    @action(detail=False, methods=('get',), url_name='orders', url_path='orders')
    def get_orders(self, request, *args, **kwargs):
        """
        Partner orders list
        """
        url = validate_url(request.data)

        order = Order.objects.filter(ordered_items__product_info__shop__url=url).exclude(state='basket').\
            prefetch_related(
            'ordered_items__product_info__product__category',
            'ordered_items__product_info__shop',
            'ordered_items__product_info__product_parameters__parameter').select_related('contact').annotate(
            summa=Sum(F('ordered_items__quantity') * F('ordered_items__product_info__price'),
                      output_field=DecimalField(max_digits=20, decimal_places=2))
        ).distinct()

        if order:
            serializer = OrderSerializer(order, many=True, context={'request': request})
            return Response(serializer.data, status=http_status.HTTP_200_OK)

        return JsonResponse({'message': 'no orders'}, status=http_status.HTTP_404_NOT_FOUND)


class ShopViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Shops list
    """
    queryset = Shop.objects
    filterset_fields = ('state',)
    ordering_fields = ('name', 'id',)
    search_fields = ('name',)
    ordering = ('name',)

    serializer_classes = {
        'list': ShopSerializer,
        'retrieve': ShopDetailSerializer,
    }
    default_serializer_class = ShopSerializer

    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.default_serializer_class)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Category list
    """
    queryset = Category.objects
    filterset_fields = ('name',)
    ordering_fields = ('name', 'id',)
    search_fields = ('name',)
    ordering = ('name',)

    serializer_classes = {
        'list': CategorySerializer,
        'retrieve': CategoryDetailSerializer,
    }
    default_serializer_class = CategorySerializer

    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.default_serializer_class)


class ProductInfoViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Products Search
    """

    queryset = ProductInfo.objects
    serializer_class = ProductInfoSerializer
    search_fields = ('product__name', 'shop__name',)

    def get_queryset(self):
        query = Q(shop__state=True)
        shop_id = self.request.query_params.get('shop_id')
        category_id = self.request.query_params.get('category_id')

        if shop_id:
            query = query & Q(shop_id=shop_id)

        if category_id:
            query = query & Q(product__category_id=category_id)

        return ProductInfo.objects.filter(
            query).select_related(
            'shop', 'product__category').prefetch_related(
            'product_parameters__parameter').distinct()


class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Work with orders - list my orders, todo: place order
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(
            user_id=self.request.user.id).exclude(state='basket').prefetch_related(
            'ordered_items__product_info__shop',
            'ordered_items__product_info__product__category',
            'ordered_items__product_info__product_parameters__parameter').select_related('contact').annotate(
            summa=Sum(F('ordered_items__quantity') * F('ordered_items__product_info__price'),
                      output_field=DecimalField(max_digits=20, decimal_places=2))).distinct()
