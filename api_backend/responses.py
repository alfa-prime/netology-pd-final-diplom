from rest_framework.response import Response
from rest_framework import status as http_status


def ResponseOK(**kwargs):
    response = {'status': 'ok'}
    if kwargs:
        response.update(kwargs)
    return Response(response, status=http_status.HTTP_200_OK)


def ResponseNotFound(**kwargs):
    response = {'status': 'not found'}
    if kwargs:
        response.update(kwargs)
    return Response(response, status=http_status.HTTP_404_NOT_FOUND)


def ResponseBadRequest(**kwargs):
    response = {'status': 'bad request'}
    if kwargs:
        response.update(kwargs)
    return Response(response, status=http_status.HTTP_400_BAD_REQUEST)
