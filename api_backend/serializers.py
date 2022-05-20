from rest_framework import serializers

from api_backend.models import Shop


class ShopsListSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Shop
        fields = ('id', 'name', 'state', 'url', 'api_url')
        read_only_fields = ('api_url', 'id')


class ShopDetailSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Shop
        exclude = ['user', 'api_url']
        read_only_fields = ('id',)
