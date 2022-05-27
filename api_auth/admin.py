from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from api_auth.models import Contact, CONTACT_ITEMS_LIMIT, User

admin.site.site_header = "Netology PD-Diplom Admin"
admin.site.site_title = "Netology PD-Diplom Admin Portal"
admin.site.index_title = "Welcome to Netology PD-Diplom Portal"


class ContactInline(admin.StackedInline):
    model = Contact
    extra = 0
    max_num = CONTACT_ITEMS_LIMIT


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    user control panel
    """
    model = User
    save_on_top = True

    fieldsets = (
        (None, {'fields': ('email', 'password', 'type')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'company', 'position')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    list_display = ('email', 'first_name', 'last_name', 'is_active', 'is_superuser')
    list_editable = ('is_active', 'is_superuser')
    list_filter = ('is_active', 'is_superuser')
    inlines = (ContactInline,)


admin.site.unregister(Group)
