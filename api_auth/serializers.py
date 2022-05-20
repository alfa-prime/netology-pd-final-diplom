from rest_framework import serializers

from api_auth.models import User, Contact
from api_backend.models import Category


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ['username', 'password']


class ContactSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.id')

    class Meta:
        model = Contact
        fields = '__all__'
