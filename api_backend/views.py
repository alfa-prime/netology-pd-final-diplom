import json

from django.db import IntegrityError
from django.db.models import Q, Sum, F, DecimalField
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from api_backend.models import Shop, Category, ProductInfo, Order, OrderItem
from api_backend.responses import ResponseOK, ResponseNotFound, ResponseBadRequest
from api_backend.serializers import ShopDetailSerializer, ShopSerializer, CategorySerializer, \
    CategoryDetailSerializer, ProductInfoSerializer, OrderSerializer, StateSerializer, ShowBasketSerializer, \
    AddOrderItemSerializer, CreateOrderSerializer
from api_backend.services import upload_partner_data, validate_url
from api_backend.tasks import send_mail_order_accepted, celery_upload_partner_data


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
            return ResponseBadRequest(message='only for shops')
        url = validate_url(request.data)
        # upload_partner_data(url, None, request.user.id)
        celery_upload_partner_data(url, None, request.user.id)
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

        return ProductInfo.objects. \
            filter(query). \
            select_related('shop', 'product__category'). \
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

    @staticmethod
    def _check_input_items_values(data):
        items_string = data.get('items')
        if items_string and items_string != 'null':
            try:
                items = json.loads(items_string)
            except (ValueError, TypeError):
                return False
        else:
            items = [data]
        return items

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

    def post(self, request, *args, **kwargs):
        """
        add products to basket
        """
        items = self._check_input_items_values(request.data)
        if not items:
            return ResponseBadRequest(message='invalid request format')

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
        return ResponseOK(message='products successfully added to basket', order_id=basket.id)

    def put(self, request, *args, **kwargs):
        """
        edit product quantity in basket
        """
        items = self._check_input_items_values(request.data)
        if not items:
            return ResponseBadRequest(message='invalid request format')

        # try:
        basket, _ = Order.objects.get_or_create(user_id=request.user.id, state='basket')
        result = {
            'update_successful': [],
            'not_found': [],
        }

        for item in items:
            order_item = OrderItem.objects.filter(order_id=basket.id, id=item['id'])
            if order_item:
                order_item.update(quantity=item['quantity'])
                result['update_successful'].append(item['id'])
            else:
                result['not_found'].append(item['id'])

        # except Exception:
        #     ResponseBadRequest(message='invalid request format.')

        return ResponseOK(result=result)

    @staticmethod
    def delete(request, *args, **kwargs):
        """
        delete products from basket
        """
        items_string = request.data.get('items')
        if not items_string or type(items_string) != str:
            return ResponseBadRequest(message='invalid request format')
        items_list = items_string.split(',')
        items_list = [item.replace(' ', '') for item in items_list]

        basket, _ = Order.objects.get_or_create(user_id=request.user.id, state='basket')
        query = Q()
        for order_item_id in items_list:
            if not order_item_id.isdigit():
                return ResponseBadRequest(message='wrong data', data=order_item_id)
            query = query | Q(order_id=basket.id, id=order_item_id)
        try:
            OrderItem.objects.filter(query).delete()
        except ValueError as e:
            return ResponseBadRequest(message=e)
        return ResponseOK(message='Ok!')


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

    @staticmethod
    def create(request, *args, **kwargs):
        serializer = CreateOrderSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        user_id = request.user.id

        try:
            order = Order.objects.get(user_id=user_id, state='basket')
        except Order.DoesNotExist:
            return ResponseBadRequest(message='basket is empty')

        try:
            updated = Order.objects.filter(user_id=user_id, id=order.id).update(contact_id=data['contact'], state='new')
        except IntegrityError:
            return ResponseBadRequest(message='wrong arguments')
        else:
            if updated:
                send_mail_order_accepted(order_id=order.id, user_name=request.user, user_email=request.user.email)
        return ResponseOK(message='Ok!')
