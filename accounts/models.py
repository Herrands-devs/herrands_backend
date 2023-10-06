import uuid
from django.contrib.auth.base_user import BaseUserManager
from django.db import models
from django.contrib.auth.models import AbstractUser,  Group, Permission
#from django.utils.translation import ugettext_lazy as _
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField



class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """

    def create_user(self, email, password, user_type, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email)
        extra_fields.setdefault('user_type', user_type)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        if user_type == 'Agent':
            user.is_agent = True
        elif user_type == 'Customer':
            user.is_customer = True

        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email, password, user_type="Customer", **extra_fields)

USER_TYPE = (('Agent', 'Agent'), ('Customer', 'Customer'))
class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = None
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    phone_number = PhoneNumberField(unique=True)
    is_agent = models.BooleanField(default=False)
    is_customer = models.BooleanField(default=False)
    user_type = models.CharField(max_length=20, choices=USER_TYPE)
    otp = models.CharField(max_length=6, null=True, blank=True)


    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()
    groups = models.ManyToManyField(
        Group,
        verbose_name=_('groups'),
        blank=True,
        related_name='custom_user_groups'  # Change this name to something unique
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('user permissions'),
        blank=True,
        related_name='custom_user_permissions'  # Change this name to something unique
    )

    def __str__(self):
        return self.email

class Agent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)

    def __str__(self):
        return str(self.user)
