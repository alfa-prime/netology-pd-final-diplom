from django.contrib import admin
from django.forms import forms
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.contrib import messages

from nested_inline.admin import NestedStackedInline, NestedModelAdmin, NestedTabularInline
from admin_extra_buttons.decorators import button
from admin_extra_buttons.mixins import ExtraButtonsMixin

from api_backend.models import Shop, Category, ProductInfo, Product, Parameter, ProductParameter, OrderItem, Order
from api_backend.services import upload_partner_data
from api_backend.tasks import celery_upload_partner_data


@admin.register(Shop)
class ShopAdmin(ExtraButtonsMixin, admin.ModelAdmin):
    list_display = ('name', 'url', 'state', 'user')
    list_filter = ('state',)
    search_fields = ('name',)
    list_editable = ('state',)

    @button(label='import', permission=lambda request, obj: request.user.type == 'shop')
    def upload(self, request):
        context = self.get_common_context(request, title='Import products')
        if request.method == 'POST':
            form = UploadForm(request.POST, request.FILES)

            if form.is_valid():
                uploaded_file = request.FILES['docfile'].read()
                # upload_partner_data(None, uploaded_file, request.user.id)
                celery_upload_partner_data(None, uploaded_file, request.user.id)
                messages.success(request, 'Price list successfully update')
                return redirect(admin_urlname(context['opts'], 'changelist'))
        else:
            form = UploadForm()
        context['form'] = form
        return TemplateResponse(request, 'admin_extra_buttons/upload.html', context)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'display_all_shops')
    list_filter = ('name',)
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
class ProductAdmin(NestedModelAdmin):
    list_display = ('name', 'category')
    list_filter = ('category',)
    search_fields = ('name',)
    save_on_top = True
    inlines = (ProductInfoInline,)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'dt', 'state', 'contact')
    list_filter = ('state',)
    save_on_top = True
    date_hierarchy = 'dt'
    inlines = (OrderItemInline,)
