from django.contrib import admin

from api_backend.models import Shop, Category, ProductInfo, Product, Parameter, ProductParameter
from nested_inline.admin import NestedStackedInline, NestedModelAdmin, NestedTabularInline


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'state', 'user')
    list_filter = ('state',)
    search_fields = ('name',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'display_all_shops')
    search_fields = ('name',)


@admin.register(Parameter)
class ParameterAdmin(admin.ModelAdmin):
    pass


class ProductParameterInline(NestedTabularInline):
    model = ProductParameter
    extra = 0


class ProductInfoInline(NestedStackedInline):
    model = ProductInfo
    extra = 0
    inlines = (ProductParameterInline,)


@admin.register(Product)
class ProductAdmin(NestedModelAdmin):
    inlines = (ProductInfoInline,)
