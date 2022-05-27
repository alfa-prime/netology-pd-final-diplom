from rest_framework.response import Response
from rest_framework import status as http_status


def ResponseBase(status, code, **kwargs):
    response = {'status': status}
    if kwargs:
        response.update(kwargs)
    return Response(response, status=code)


def ResponseOK(**kwargs):
    return ResponseBase('ok', http_status.HTTP_200_OK, **kwargs)


def ResponseNotFound(**kwargs):
    return ResponseBase('not found', http_status.HTTP_404_NOT_FOUND, **kwargs)


def ResponseBadRequest(**kwargs):
    return ResponseBase('bad request', http_status.HTTP_400_BAD_REQUEST, **kwargs)
