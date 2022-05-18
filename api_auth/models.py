from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

from api_auth.managers import UserManager

USER_TYPE_CHOICES = (
    ('shop', _('Shop')),
    ('buyer', _('Buyer')),
)

CONTACT_ITEMS_LIMIT = 5


class User(AbstractUser):
    """
    User model
    """
    REQUIRED_FIELDS = ['last_name', 'first_name', 'patronymic', 'company', 'position', 'type']
    objects = UserManager()
    username_validator = UnicodeUsernameValidator()
    USERNAME_FIELD = 'email'

    email = models.EmailField(_('email address'), help_text=_('Enter email address'), unique=True)
    last_name = models.CharField(_('last name'), max_length=40, blank=True)
    first_name = models.CharField(_('first name'), max_length=40, blank=True)
    patronymic = models.CharField(_('patronymic'), max_length=40, blank=True)
    company = models.CharField(_('company'), help_text=_('Enter company name'), max_length=40, blank=True)
    position = models.CharField(_('position'), help_text=_('Enter user position in company'), max_length=40, blank=True)
    type = models.CharField(_('user type'), choices=USER_TYPE_CHOICES, max_length=10, default='buyer')
    username = models.CharField(
        _('username'),
        max_length=150,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    is_active = models.BooleanField(
        _('active'),
        default=False,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )

    def __str__(self):
        return f'{self.first_name} {self.last_name}'
        # return f'{self.first_name} {self.last_name} {self.email}'

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ('email',)


class Contact(models.Model):
    """
    User contact model
    """
    user = models.ForeignKey(User, verbose_name=_('user'), related_name='contacts', on_delete=models.CASCADE)
    person = models.CharField(_('contact person'), help_text=_('Enter contact person'), max_length=50, blank=True)
    phone = PhoneNumberField(_('phone'), help_text=_('Enter phone number'), null=True, blank=True)
    city = models.CharField(_('city'), help_text=_('Enter city name'), max_length=50, blank=True)
    street = models.CharField(_('street'), help_text=_('Enter street name'), max_length=100, blank=True)
    house = models.CharField(_('house'), max_length=15, blank=True)
    structure = models.CharField(_('structure'), max_length=15, blank=True)
    building = models.CharField(_('building'), max_length=15, blank=True)
    apartment = models.CharField(_('apartment'), max_length=15, blank=True)

    def save(self, *args, **kwargs):
        if self.user.contacts.count() < CONTACT_ITEMS_LIMIT or self.user.contacts.filter(id=self.id).exists():
            super(Contact, self).save(*args, **kwargs)
        else:
            raise ValidationError(f'There are already {CONTACT_ITEMS_LIMIT} contacts. No more are allowed')

    def __str__(self):
        return f'{self.person}, {self.phone}, ' \
               f'{self.city} {self.street} {self.house} {self.structure} {self.building} {self.apartment}'
        # return f'{self.user}: {self.person} /{self.phone}/ ' \
        #        f'{self.city} {self.street} {self.house} {self.structure} {self.building} {self.apartment}'

    class Meta:
        db_table = 'contacts'
        verbose_name = _('Contact')
        verbose_name_plural = _('Individual contacts')
