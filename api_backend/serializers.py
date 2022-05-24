from rest_framework import serializers
from api_auth.models import Contact

from api_backend.mixins import ModelPresenter
from api_backend.models import Shop, Category, ProductInfo, Product, ProductParameter, Order, OrderItem


class ShopsListSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Shop
        fields = ('id', 'name', 'api_url')
        read_only_fields = ('api_url', 'id')


class ShopDetailSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Shop
        fields = ('id', 'name', 'url', 'state')
        read_only_fields = ('id',)


class CategoryListSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'api_url')
        read_only_fields = ('api_url', 'id')


class CategoryDetailSerializer(serializers.HyperlinkedModelSerializer):
    shops = ShopsListSerializer(many=True)

    class Meta:
        model = Category
        fields = ('id', 'name', 'shops')
        read_only_fields = ('api_url', 'id')


class ProductInfoSerializer(serializers.ModelSerializer):
    ShopSerializer = ModelPresenter(Shop, ('name', 'api_url'))
    ProductParameterSerializer = ModelPresenter(ProductParameter, ('parameter', 'value',),
                                                {'parameter': serializers.StringRelatedField()})
    CategorySerializer = ModelPresenter(Category, ('name', 'api_url'))
    ProductSerializer = ModelPresenter(Product, ('name', 'category',), {'category': CategorySerializer()})

    product = ProductSerializer(read_only=True)
    product_parameters = ProductParameterSerializer(read_only=True, many=True)
    shop = ShopSerializer(read_only=True)
    stock_quantity = serializers.CharField(source='quantity')

    class Meta:
        model = ProductInfo
        fields = ('product', 'shop', 'stock_quantity', 'price', 'price_rrc', 'product_parameters')
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
    order_sum = serializers.DecimalField(read_only=True, max_digits=20, decimal_places=2, min_value=0)

    class Meta:
        model = Order
        fields = ('id', 'state', 'contact', 'dt', 'order_sum', 'ordered_items',)
        read_only_fields = ('id', 'state')
