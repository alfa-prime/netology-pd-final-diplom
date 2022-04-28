from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from api_auth.managers import UserManager

USER_TYPE_CHOICES = (
    ('shop', _('Shop')),
    ('buyer', _('Buyer')),
)


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
        return f'{self.first_name} {self.last_name} {self.email}'

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'List of users'
        ordering = ('email',)
