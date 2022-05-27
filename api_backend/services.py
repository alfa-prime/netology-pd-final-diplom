import requests
from yaml import load as yaml_load, SafeLoader
from api_backend.models import Shop, Category, ProductInfo, Product, Parameter, ProductParameter
from api_backend.serializers import UrlSerializer


def upload_partner_data(url=None, file_obj=None, user_id=0):
    """
    partner price list update (file or url)
    """
    if file_obj:
        data = yaml_load(file_obj, Loader=SafeLoader)
    else:
        stream = requests.get(url).content
        data = yaml_load(stream, Loader=SafeLoader)

    shop, _ = Shop.objects.get_or_create(name=data.get('shop'), defaults={'user_id': user_id})

    for category in data['categories']:
        category_object, _ = Category.objects.get_or_create(id=category['id'], name=category['name'])
        category_object.shops.add(shop.id)
        category_object.save()

    ProductInfo.objects.filter(shop_id=shop.id).delete()

    for item in data['goods']:
        product, _ = Product.objects.get_or_create(name=item['name'], category_id=item['category'])

        product_info = ProductInfo.objects.create(product_id=product.id,
                                                  external_id=item['id'],
                                                  price=item['price'],
                                                  price_rrc=item['price_rrc'],
                                                  quantity=item['quantity'],
                                                  shop_id=shop.id)
        for name, value in item['parameters'].items():
            parameter_object, _ = Parameter.objects.get_or_create(name=name)
            ProductParameter.objects.create(product_info_id=product_info.id,
                                            parameter_id=parameter_object.id,
                                            value=value)


def validate_url(url):
    """
    url validator
    """
    serializer = UrlSerializer(data=url)
    serializer.is_valid(raise_exception=True)
    return serializer.validated_data.get('url')
