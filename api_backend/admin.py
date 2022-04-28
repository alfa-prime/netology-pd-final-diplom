from django.contrib import admin

from api_backend.models import Shop, Category


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'state', 'user')
    list_filter = ('state',)
    search_fields = ('name',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'display_all_shops')
    search_fields = ('name',)

