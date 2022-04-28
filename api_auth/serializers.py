from rest_framework import serializers

from api_auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ['username', 'password']
