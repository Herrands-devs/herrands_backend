from django.db import models
import uuid
from django.conf import settings
from django.contrib.auth import get_user_model
from phonenumber_field.modelfields import PhoneNumberField
# Create your models here.

'''class VehicleType(models.Model):
    vehicle = models.CharField()

    def __str__(self):
        return self.vehicle'''

class VehicleMetric(models.Model):
    vehicle_type = models.CharField(max_length=200)
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return self.vehicle_type

class DistanceMetric(models.Model):
    rate_per_km = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return self.rate_per_km

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Subtype(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return self.name



class File(models.Model):
    file = models.FileField(upload_to='task_files/')

    def __str__(self):
        return self.file.name

class ErrandTask(models.Model):
    REQUESTED = 'REQUESTED'
    REJECTED = 'REJECTED'
    ACCEPTED = 'ACCEPTED'
    ARRIVED = 'ARRIVED'
    STARTED = 'STARTED'
    IN_PROGRESS = 'IN_PROGRESS'
    COMPLETED = 'COMPLETED'
    STATUSES = (
        (REQUESTED, REQUESTED),
        (REJECTED, REJECTED),
        (ACCEPTED, ACCEPTED),
        (ARRIVED,ARRIVED),
        (STARTED, STARTED),
        (IN_PROGRESS, IN_PROGRESS),
        (COMPLETED, COMPLETED),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    state_within = models.CharField(max_length=100, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    subtype = models.ForeignKey(Subtype, on_delete=models.CASCADE)
    pick_up_address = models.CharField(max_length=255, null=True, blank=True)
    pick_up_lat = models.DecimalField(max_digits=30, decimal_places=15, null=True, blank=True)
    pick_up_long = models.DecimalField(max_digits=30, decimal_places=15, null=True, blank=True)
    drop_off_address = models.CharField(max_length=255, null=True, blank=True)
    drop_off_lat = models.DecimalField(max_digits=30, decimal_places=15, null=True, blank=True)
    drop_off_long = models.DecimalField(max_digits=30, decimal_places=15, null=True, blank=True)
    recipient_contact = PhoneNumberField(null=True, blank=True)
    sender_contact = PhoneNumberField(null=True, blank=True)
    item_description = models.TextField(null=True, blank=True)
    grocery_list = models.JSONField(blank=True, null=True)
    grocery_estimated_price = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    describe_errand = models.TextField(null=True, blank=True)
    how_long = models.PositiveIntegerField(null=True, blank=True)
    due_date = models.DateTimeField(blank=True, null=True)
    files = models.ManyToManyField(File, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUSES, default=REQUESTED)
    user_cancelled = models.BooleanField(default=False)
    agent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='errands_as_agent'
    )
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='errands_as_customer'
    )
    rejected_agents = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        related_name='errands_rejected'
    )
    vehicle_type = models.ForeignKey(VehicleMetric, on_delete=models.SET_NULL, null=True, blank=True)
    distance_in_km = models.FloatField(null=True, blank=True)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f'{self.id}'

    def get_absolute_url(self):
        return reverse('errand:errand_detail', kwargs={'errand_id': self.id})