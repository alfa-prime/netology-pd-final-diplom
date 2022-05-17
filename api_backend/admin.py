from django.contrib import admin
from django.forms import forms
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.contrib.admin.templatetags.admin_urls import admin_urlname

from nested_inline.admin import NestedStackedInline, NestedModelAdmin, NestedTabularInline
from admin_extra_buttons.decorators import button
from admin_extra_buttons.mixins import ExtraButtonsMixin
from yaml import load as yaml_load, SafeLoader

from api_backend.models import Shop, Category, ProductInfo, Product, Parameter, ProductParameter
from api_backend.services import partner_update


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
    search_fields = ('name',)
    save_on_top = True
    inlines = (ProductInfoInline,)

    @button(label='import', permission=lambda request, obj: request.user.type == 'shop')
    def upload(self, request):
        context = self.get_common_context(request, title='Import products')
        if request.method == 'POST':
            form = UploadForm(request.POST, request.FILES)

            if form.is_valid():
                uploaded_file = request.FILES['docfile'].read()
                data = yaml_load(uploaded_file, SafeLoader)
                user_id = request.user.id
                partner_update(user_id=user_id, data=data)
                return redirect(admin_urlname(context['opts'], 'changelist'))
        else:
            form = UploadForm()
        context['form'] = form
        return TemplateResponse(request, 'admin_extra_buttons/upload.html', context)
