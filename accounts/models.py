import uuid
from django.contrib.auth.base_user import BaseUserManager
from django.db import models
from django.contrib.auth.models import AbstractUser,  Group, Permission
#from django.utils.translation import ugettext_lazy as _
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField
from django_countries.fields import CountryField



class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """

    def create_user(self, email, user_type, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email)
        extra_fields.setdefault('user_type', user_type)
        user = self.model(email=email, **extra_fields)
        #user.set_password(password)
        if user_type == 'Agent':
            user.is_agent = True
        elif user_type == 'Customer':
            user.is_customer = True

        user.save()
        return user

        '''def create_superuser(self, email, password, **extra_fields):
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
        return self.create_user(email, password, phone_number="+2348055343594", **extra_fields)'''
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
        return self.create_user(email, password,phone_number="+2348055343591", **extra_fields)



USER_TYPE = (('Admin','Admin'),('Agent', 'Agent'), ('Customer', 'Customer'))
STATUS = (('Active', 'Active'), ('Suspended', 'Suspended'), ('Banned', 'Banned'), ('Pending', 'Pending'))
class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = None
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    phone_number = PhoneNumberField(unique=True)
    current_lat = models.DecimalField(max_digits=30, decimal_places=15, null=True, blank=True)
    current_long = models.DecimalField(max_digits=30, decimal_places=15, null=True, blank=True)
    current_location = models.TextField(max_length=200, null=True, blank=True)
    is_agent = models.BooleanField(default=False)
    is_customer = models.BooleanField(default=False)
    user_type = models.CharField(max_length=20, choices=USER_TYPE)
    otp = models.CharField(max_length=6, null=True, blank=True)
    account_completed = models.BooleanField(default=False)
    status = models.CharField(max_length=100, null=True, blank=True, choices=STATUS, default='Active')


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






class Preferences(models.Model):
    title = models.CharField(max_length=100)

    def __str__(self):
        return str(self.title)

class Services(models.Model):
    title = models.CharField(max_length=100)

    def __str__(self):
        return str(self.title)

class Idtype(models.Model):
    title = models.CharField(max_length=100)

    def __str__(self):
        return str(self.title)

class Agent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    country = CountryField(blank=True, null=True)
    state = models.CharField(null=True, blank=True, max_length=100)
    preference = models.ForeignKey(
        Preferences,
        on_delete=models.DO_NOTHING,
        related_name='preferece_as_agent' 
    )
    services = models.ManyToManyField(
        Services,
        related_name='services_as_agent'
    )
    id_type = models.ForeignKey(
        Idtype,
        on_delete=models.DO_NOTHING,
        related_name='id_type' 
    )
    id_file = models.FileField(blank=False, null=False, upload_to='uploads/agents-documents')
    photo = models.URLField(null=True, blank=True)
    pay_per_hour = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    arrival_speed = models.IntegerField(help_text="How fast can you drive in km/h?", null=True, blank=True)
    delivery_speed = models.IntegerField(help_text="How fast can you drive in km/h?", null=True, blank=True)
    bank_name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=30)
    beneficiary_name = models.CharField(max_length=30, null=True, blank=True)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    
    

    def __str__(self):
        return str(self.user)

