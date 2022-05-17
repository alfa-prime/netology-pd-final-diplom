from django.contrib import admin
from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.forms import forms
from django.shortcuts import redirect
from django.template.response import TemplateResponse

from admin_extra_buttons.decorators import button
from admin_extra_buttons.mixins import ExtraButtonsMixin

from yaml import load as yaml_load, SafeLoader

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


class UploadForm(forms.Form):
    docfile = forms.FileField(label='Select a file')


@admin.register(Product)
class ProductAdmin(ExtraButtonsMixin, NestedModelAdmin):
    inlines = (ProductInfoInline,)

    @button(label='import')
    def upload(self, request):
        context = self.get_common_context(request, title='Import products')
        if request.method == 'POST':
            form = UploadForm(request.POST, request.FILES)
            if form.is_valid():
                uploaded_file = request.FILES['docfile'].read()
                data = yaml_load(uploaded_file, SafeLoader)

                user_id = request.user.id
                shop = data.get('shop')
                categories = data.get('categories', [])
                goods = data.get('goods', [])

                shop, _ = Shop.objects.get_or_create(name=shop, defaults={'user_id': user_id})

                for category in categories:
                    category_obj, _ = Category.objects.get_or_create(name=category.get('name'))
                    category_obj.shops.add(shop.id)
                    category_obj.save()

                ProductInfo.objects.filter(shop_id=shop.id).delete()

                for item in goods:
                    category_obj, _ = Category.objects.get_or_create(name=item.get('category'))
                    product, _ = Product.objects.get_or_create(name=item.get('name'), category_id=category_obj.id)

                    product_info = ProductInfo.objects.create(product_id=product.id,
                                                              external_id=item.get('id'),
                                                              price=item.get('price'),
                                                              price_rrc=item.get('price_rrc'),
                                                              quantity=item.get('quantity'),
                                                              shop_id=shop.id)
                    for entry in item.get('parameters', []):
                        parameter_object, _ = Parameter.objects.get_or_create(name=entry.get('name'))
                        ProductParameter.objects.create(product_info_id=product_info.id,
                                                        parameter_id=parameter_object.id,
                                                        value=entry.get('value'))

                return redirect(admin_urlname(context['opts'], 'changelist'))
        else:
            form = UploadForm()
        context['form'] = form
        return TemplateResponse(request, 'admin_extra_buttons/upload.html', context)
