from django.db import models
from django.utils.translation import gettext_lazy as _

from core import settings


class Shop(models.Model):
    name = models.CharField(max_length=50, verbose_name=_('shop name'), unique=True)
    url = models.URLField(verbose_name='Url', null=True, blank=True)
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
    name = models.CharField(max_length=50, verbose_name='Category name')
    shops = models.ManyToManyField(Shop, blank=True, verbose_name='Shops', related_name='categories')

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

    def __str__(self):
        return self.name

    def display_all_shops(self):
        return ', '.join([shop.name for shop in self.shops.all()])

    display_all_shops.short_description = 'shops'
