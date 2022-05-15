from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from core import settings


class Shop(models.Model):
    name = models.CharField(max_length=50, verbose_name=_('shop name'), unique=True)
    url = models.URLField(verbose_name='url', null=True, blank=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, verbose_name='user name',
                                blank=True, null=True,
                                on_delete=models.CASCADE)

    state = models.BooleanField(verbose_name=_('order receipt status'), default=True)

    class Meta:
        db_table = 'shops'
        verbose_name = _('Shop')
        verbose_name_plural = _('List of shops')
        ordering = ('-name',)

    def __str__(self):
        return f'{self.name} ({self.user})'


class Category(models.Model):
    name = models.CharField(max_length=50, verbose_name='category name')
    shops = models.ManyToManyField(Shop, blank=True, verbose_name='shops', related_name='categories')

    class Meta:
        db_table = 'categories'
        verbose_name = 'Category'
        verbose_name_plural = 'List of categories'
        ordering = ('-name',)

    def __str__(self):
        return self.name

    def display_all_shops(self):
        return ', '.join([shop.name for shop in self.shops.all()])

    display_all_shops.short_description = 'shops'


class Product(models.Model):
    name = models.CharField(max_length=80, verbose_name=_('product name'))
    category = models.ForeignKey(Category, verbose_name=_('category'), related_name='products', blank=True,
                                 on_delete=models.CASCADE)

    class Meta:
        db_table = 'products'
        verbose_name = _('Product')
        verbose_name_plural = _('List of products')
        ordering = ('-name',)

    def __str__(self):
        return self.name


class ProductInfo(models.Model):
    external_id = models.PositiveIntegerField(verbose_name=_('external id'))
    product = models.ForeignKey(Product, verbose_name=_('product'), related_name='product_infos', blank=True,
                                on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop, verbose_name=_('shop'), related_name='product_infos', blank=True,
                             on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(verbose_name=_('quantity'))
    price = models.DecimalField(max_digits=20, decimal_places=2, verbose_name=_('price'),
                                validators=[MinValueValidator(0)])
    price_rrc = models.DecimalField(max_digits=20, decimal_places=2, verbose_name=_('recommended retail price'),
                                    validators=[MinValueValidator(0)])

    class Meta:
        db_table = 'product_info'
        verbose_name = _('Product info')
        verbose_name_plural = _('Product info list')
        constraints = [
            models.UniqueConstraint(fields=['product', 'shop', 'external_id'], name='unique_product_info'),
        ]

    def __str__(self):
        return f'{self.shop}: {self.product}'


class Parameter(models.Model):
    name = models.CharField(max_length=40, verbose_name=_('name'), unique=True)

    class Meta:
        db_table = 'parameters'
        verbose_name = _('Parameters')
        verbose_name_plural = _('List of parameters')
        ordering = ('-name',)

    def __str__(self):
        return self.name


class ProductParameter(models.Model):
    product_info = models.ForeignKey(ProductInfo, verbose_name=_('product info'),  related_name='product_parameters',
                                     blank=True, on_delete=models.CASCADE)
    parameter = models.ForeignKey(Parameter, verbose_name=_('parameter'), related_name='product_parameters', blank=True,
                                  on_delete=models.CASCADE)
    value = models.CharField(verbose_name=_('value'), max_length=100)

    class Meta:
        verbose_name = _('Parameter')
        verbose_name_plural = _('Parameters')
        constraints = [
            models.UniqueConstraint(fields=['product_info', 'parameter'], name='unique_product_parameter'),
        ]

    def __str__(self):
        return f'{self.parameter} [ {self.product_info} ]'
