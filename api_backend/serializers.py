from rest_framework import serializers

from api_backend.models import Shop, Category, ProductInfo, Product


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


class ShopDetailCategoryListSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Shop
        fields = ('id', 'name', 'api_url')
        read_only_fields = ('api_url', 'id')


class CategoryListSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'api_url')
        read_only_fields = ('api_url', 'id')


class CategoryDetailSerializer(serializers.HyperlinkedModelSerializer):
    shops = ShopDetailCategoryListSerializer(many=True)

    class Meta:
        model = Category
        fields = ('id', 'name', 'shops')
        read_only_fields = ('api_url', 'id')


class ProductSerializer(serializers.ModelSerializer):
    category = CategoryListSerializer(read_only=True)

    class Meta:
        model = Product
        fields = ('id', 'name', 'category')


class ProductInfoSerializer(serializers.ModelSerializer):
    shop = ShopsListSerializer(read_only=True)
    product = ProductSerializer(read_only=True)

    class Meta:
        model = ProductInfo
        fields = ('product', 'shop', 'quantity', 'price', 'price_rrc', 'api_url')




