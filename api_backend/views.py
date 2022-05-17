from django.core.validators import URLValidator
from django.http import JsonResponse

from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView

import requests
from yaml import load as yaml_load, SafeLoader

from api_backend.services import partner_update


class PartnerUpdate(APIView):
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Status': False, 'Error': 'Log in required'}, status=403)

        if request.user.type != 'shop':
            return JsonResponse({'Status': False, 'Error': 'Only for shops'}, status=403)

        url = request.data.get('url')

        if url:
            validate_url = URLValidator()
            try:
                validate_url(url)
            except ValidationError as e:
                return JsonResponse({'Status': False, 'Error': str(e)})
            else:
                stream = requests.get(url).content
                data = yaml_load(stream, Loader=SafeLoader)
                user_id = request.user.id
                partner_update(user_id=user_id, data=data)
                return JsonResponse({'Status': True, 'Message': 'Price list successfully update'})

        return JsonResponse({'Status': False, 'Errors': 'All necessary arguments are not specified'})
