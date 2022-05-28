from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from api_auth.models import Contact, User

from api_backend.mixins import ModelPresenter
from api_backend.models import Shop, Category, ProductInfo, Product, ProductParameter, Order, OrderItem


class UrlSerializer(serializers.Serializer): # noqa
    url = serializers.URLField()


class StateSerializer(serializers.Serializer): # noqa
    state = serializers.CharField()

    def validate_state(self, value): # noqa
        if value not in ['on', 'off']:
            raise ValidationError('Only on or off')
        return value


class ShopSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Shop
        fields = ('id', 'name', 'state', 'url', 'api_url')
        read_only_fields = ('api_url', 'id')


class ShopDetailSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Shop
        fields = ('id', 'name', 'state', 'url')
        read_only_fields = ('id',)


class CategorySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'api_url')
        read_only_fields = ('api_url', 'id')


class CategoryDetailSerializer(serializers.HyperlinkedModelSerializer):
    shops = ShopSerializer(many=True)

    class Meta:
        model = Category
        fields = ('id', 'name', 'shops')
        read_only_fields = ('api_url', 'id')


class ProductInfoSerializer(serializers.HyperlinkedModelSerializer):
    ShopSerializer = ModelPresenter(Shop, ('id', 'name', 'api_url'))
    ProductParameterSerializer = ModelPresenter(ProductParameter, ('parameter', 'value',),
                                                {'parameter': serializers.StringRelatedField()})
    CategorySerializer = ModelPresenter(Category, ('id', 'name', 'api_url'))
    ProductSerializer = ModelPresenter(Product, ('id', 'name', 'category',), {'category': CategorySerializer()})

    product = ProductSerializer(read_only=True)
    product_parameters = ProductParameterSerializer(read_only=True, many=True)
    shop = ShopSerializer(read_only=True)
    stock_quantity = serializers.CharField(source='quantity')
    # product_id_for_order = serializers.CharField(source='id')

    class Meta:
        model = ProductInfo
        fields = ('id', 'product', 'product_parameters', 'shop', 'stock_quantity', 'price', 'price_rrc', )
        read_only_fields = ('id',)


class OrderedItemsSerializer(serializers.ModelSerializer):
    product_info = ProductInfoSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ('product_info', 'quantity',)


class OrderSerializer(serializers.HyperlinkedModelSerializer):
    ContactSerializer = ModelPresenter(Contact, ('person', 'phone'))
    OrderedItemsSerializer = ModelPresenter(OrderItem, ('quantity', 'product_info'),
                                            {'product_info': ProductInfoSerializer()})

    contact = ContactSerializer(read_only=True)
    ordered_items = OrderedItemsSerializer(read_only=True, many=True)
    summa = serializers.DecimalField(read_only=True, max_digits=20, decimal_places=2, min_value=0)

    class Meta:
        model = Order
        fields = ('id', 'state', 'contact', 'dt', 'summa', 'ordered_items',)
        read_only_fields = ('id', 'state')


class ShowBasketSerializer(serializers.HyperlinkedModelSerializer):
    ShopSerializer = ModelPresenter(Shop, ('id', 'api_url', 'name',))
    ProductInfoSerializer = ModelPresenter(ProductInfo, ('id', 'api_url', 'product', 'shop', 'price', 'price_rrc'),
                                           {'product': serializers.StringRelatedField(), 'shop': ShopSerializer()})
    OrderedItemsSerializer = ModelPresenter(OrderItem, ('id', 'product_info', 'quantity'),
                                            {'product_info': ProductInfoSerializer()})

    ordered_items = OrderedItemsSerializer(read_only=True, many=True)
    total_sum = serializers.DecimalField(read_only=True, max_digits=20, decimal_places=2, min_value=0)

    class Meta:
        model = Order
        fields = ('ordered_items', 'total_sum')


class AddOrderItemSerializer(serializers.HyperlinkedModelSerializer):
    items = serializers.JSONField(required=False)
    product_info = serializers.PrimaryKeyRelatedField(
        queryset=ProductInfo.objects.select_related('shop', 'product').prefetch_related('shop__user').all())

    class Meta:
        model = OrderItem
        fields = ('product_info', 'quantity', 'items',)


class CreateOrderSerializer(serializers.HyperlinkedModelSerializer):
    class KeyField(serializers.PrimaryKeyRelatedField):
        def get_queryset(self):
            return self.context['request'].user.contacts.all()

    contact = KeyField(required=True, read_only=False, allow_null=False)

    class Meta:
        model = Order
        fields = ('contact',)
        write_only_fields = ('contact',)
        extra_kwargs = {'contact': {'required': True, 'allow_null': False}}
