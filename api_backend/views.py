import json
from django.db import IntegrityError
from django.db.models import Q, Sum, F, DecimalField
from rest_framework import viewsets
from rest_framework.decorators import action
from django.core.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated

from api_backend.models import Shop, Category, ProductInfo, Order, OrderItem
from api_backend.responses import ResponseOK, ResponseNotFound, ResponseBadRequest
from api_backend.serializers import ShopDetailSerializer, ShopSerializer, CategorySerializer, \
    CategoryDetailSerializer, ProductInfoSerializer, OrderSerializer, StateSerializer, ShowBasketSerializer, \
    AddOrderItemSerializer
from api_backend.services import upload_partner_data, validate_url


class PartnerViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=('get', 'put'), url_name='state', url_path='state')
    def state(self, request, *args, **kwargs):
        """
        change shop orders receipt status (on/off)
        """
        if request.method == 'GET':
            url = validate_url(request.data)
            shop = Shop.objects.filter(url=url).first()
            if shop:
                return ResponseOK(shop_state=shop.state)
        else:
            serializer = StateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            shop = Shop.objects.filter(user_id=request.user.id).first()
            if shop:
                state = serializer.validated_data.get('state')
                shop.state = True if state == 'on' else False
                shop.save()
                return ResponseOK(shop_state=shop.state)
        return ResponseNotFound(message='shop not found')

    @action(detail=False, methods=('post',), url_name='update', url_path='update')
    def update_price_list(self, request, *args, **kwargs):
        """
        update partner price list
        """
        if request.user.type != 'shop':
            raise ValidationError({'error': 'Only for shops'})
        url = validate_url(request.data)
        upload_partner_data(url, None, request.user.id)
        return ResponseOK(message='price list successfully update')

    @action(detail=False, methods=('get',), url_name='orders', url_path='orders')
    def get_orders(self, request, *args, **kwargs):
        """
        partner orders list
        """
        url = validate_url(request.data)
        order = Order.objects.filter(ordered_items__product_info__shop__url=url).exclude(state='basket'). \
            prefetch_related(
            'ordered_items__product_info__product__category',
            'ordered_items__product_info__shop',
            'ordered_items__product_info__product_parameters__parameter').select_related('contact').annotate(
            summa=Sum(F('ordered_items__quantity') * F('ordered_items__product_info__price'),
                      output_field=DecimalField(max_digits=20, decimal_places=2))
        ).distinct()
        if order:
            serializer = OrderSerializer(order, many=True, context={'request': request})
            return ResponseOK(data=serializer.data)
        return ResponseNotFound(message='no orders')


class ShopViewSet(viewsets.ReadOnlyModelViewSet):
    """
    shops list
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
    category list
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
    products search
    """

    queryset = ProductInfo.objects
    search_fields = ('product__name', 'shop__name',)

    def get_queryset(self):
        query = Q(shop__state=True)
        shop_id = self.request.query_params.get('shop_id')
        category_id = self.request.query_params.get('category_id')

        if shop_id:
            query = query & Q(shop_id=shop_id)

        if category_id:
            query = query & Q(product__category_id=category_id)

        return ProductInfo.objects.\
            filter(query).\
            select_related('shop', 'product__category').\
            prefetch_related('product_parameters__parameter').distinct()

    def list(self, request, *args, **kwargs):
        products = self.get_queryset()
        if products:
            serializer = ProductInfoSerializer(products, many=True, context={'request': request})
            return ResponseOK(data=serializer.data)
        return ResponseNotFound(message='products not found')


class BasketViewSet(viewsets.GenericViewSet):
    """
    basket processing
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = OrderSerializer

    def get_queryset(self, *argc, **argv):
        return Order.objects.filter(
            user_id=self.request.user.id, state='basket').prefetch_related(
            'ordered_items__product_info__shop',
            'ordered_items__product_info__product__category',
            'ordered_items__product_info__product_parameters__parameter').annotate(
            total_sum=Sum(F('ordered_items__quantity') * F('ordered_items__product_info__price'),
                          output_field=DecimalField(max_digits=20, decimal_places=2)
                          )).distinct()

    def list(self, request, *args, **kwargs):
        """
        get products list in basket
        """
        basket = self.get_queryset()
        if basket:
            serializer = ShowBasketSerializer(basket, many=True, context={'request': request})
            return ResponseOK(data=serializer.data)
        return ResponseNotFound(message='no products in basket')

    @staticmethod
    def post(request, *args, **kwargs):
        """
        add products to basket
        """
        items_string = request.data.get('items')
        if items_string and items_string != 'null':
            try:
                items = json.loads(items_string)
            except (ValueError, TypeError):
                return ResponseBadRequest(message='invalid request format')
        else:
            items = [request.data]

        basket, _ = Order.objects.get_or_create(user_id=request.user.id, state='basket')

        # todo: подумать как проверить количество заказываемого товара на складе
        ordered_items = []
        for order_item in items:
            serializer = AddOrderItemSerializer(data=order_item)
            serializer.is_valid(raise_exception=True)
            data = serializer.validated_data
            data.update({'order_id': basket.id})
            ordered_items.append(OrderItem(**data))
        try:
            OrderItem.objects.bulk_create(ordered_items)
        except IntegrityError:
            return ResponseBadRequest(message='product already in basket')
        return ResponseOK(message='products successfully added to basket')

    def put(self, request, *args, **kwargs):
        ...

    def delete(self, request, *args, **kwargs):
        ...


class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    """
    work with orders - list my orders
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
