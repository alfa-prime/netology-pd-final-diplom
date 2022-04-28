from django.contrib import admin

from api_backend.models import Shop, Category, ProductInfo, Product
from nested_inline.admin import NestedStackedInline, NestedModelAdmin


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'state', 'user')
    list_filter = ('state',)
    search_fields = ('name',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'display_all_shops')
    search_fields = ('name',)


class ProductInfoInline(NestedStackedInline):
    model = ProductInfo
    extra = 0


@admin.register(Product)
class ProductAdmin(NestedModelAdmin):
    inlines = (ProductInfoInline,)
