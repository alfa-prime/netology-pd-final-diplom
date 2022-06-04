from django.core.mail import send_mail
import requests
from yaml import load as yaml_load, SafeLoader

from core.celery import app
from api_backend.models import OrderItem, Shop, Category, ProductInfo, Product, Parameter, ProductParameter


@app.task
def send_mail_order_accepted(order_id: str, user_name: str, user_email: str):
    """
    send order to buyer email
    """
    ordered_items = OrderItem.objects.filter(order__id=order_id). \
        prefetch_related('product_info', 'order', 'product_info__shop__user').all()

    subject = f'order on Netology PD-Diplom Portal'
    message = f'Dear {user_name}, your order #{order_id} has been received and accepted for work.\n' \
              f'Order items:\n'

    for item in ordered_items:
        order_item = f'{item.product_info.product}:: ' \
                     f'quantity {item.quantity}:: ' \
                     f'price {item.product_info.price}\n'
        message += order_item

    return send_mail(subject=subject, message=message, from_email=None, recipient_list=[user_email])


@app.task
def celery_upload_partner_data(url=None, file_obj=None, user_id=0):
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
