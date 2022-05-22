from rest_framework import serializers

from api_backend.models import Shop, Category


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
        fields = ('id', 'name', 'url', 'state', 'api_url')
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
