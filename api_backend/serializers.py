from rest_framework import serializers

from api_backend.models import Shop


class ShopSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Shop
        fields = ('id', 'name', 'state', 'url')
        read_only_fields = ('url', 'id', 'name',)
