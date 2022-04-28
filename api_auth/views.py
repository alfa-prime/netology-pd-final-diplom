import requests
from rest_framework.response import Response
from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def request_user_activation(request, uid, token):
    """ User activation """

    post_url = "http://127.0.0.1:8000/api/v1/users/activation/"
    post_data = {"uid": uid, "token": token}
    response = requests.post(post_url, data=post_data)
    return Response(response.text)
