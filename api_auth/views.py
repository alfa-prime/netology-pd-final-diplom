import requests
from django.core import exceptions
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.viewsets import ModelViewSet

from api_auth.models import Contact
from api_auth.serializers import ContactSerializer


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def request_user_activation(request, uid, token):
    """ User activation """

    post_url = "http://127.0.0.1:8000/api/v1/users/activation/"
    post_data = {"uid": uid, "token": token}
    response = requests.post(post_url, data=post_data)
    return Response(response.text)


class ContactViewSet(ModelViewSet):
    """ Works with user contacts [create, read, update, delete] """

    serializer_class = ContactSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.request.user.contacts.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer_class()(request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            Contact.objects.create(user=request.user, **data)
        except exceptions.ValidationError as e:
            return Response(f'{e}', status=status.HTTP_400_BAD_REQUEST)
        return Response('Created', status=status.HTTP_201_CREATED)

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        try:
            obj = queryset.get(pk=self.request.data['id'])
        except Exception:
            raise ValidationError('Contact with the specified id was not found')

        self.check_object_permissions(self.request, obj)
        return obj

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @action(methods=["DELETE"], detail=False,)
    def delete(self, request):
        items_string = request.data.get('items')

        if not items_string or type(items_string) != str:
            raise ValidationError('No items for delete')

        items_list = [item.strip() for item in items_string.split(',')]
        items_founded = Contact.objects.filter(id__in=items_list)
        items_founded_ids = [x.id for x in items_founded]
        items_founded.delete()

        return Response(f'Deleted ids: {items_founded_ids}', status=status.HTTP_200_OK)
