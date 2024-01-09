from django.db import models
import uuid
from django.conf import settings
from django.contrib.auth import get_user_model
from phonenumber_field.modelfields import PhoneNumberField
from datetime import timedelta
from django.db.models.signals import post_save
from django.dispatch import receiver
# Create your models here.

'''class VehicleType(models.Model):
    vehicle = models.CharField(max_length=200)

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
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)

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
    PICKED_UP = 'PICKED_UP'
    MONTHS= 'MONTHS'
    DAYS = 'DAYS'
    HOURS = 'HOURS'
    STATUSES = (
        (REQUESTED, REQUESTED),
        (REJECTED, REJECTED),
        (ACCEPTED, ACCEPTED),
        (ARRIVED,ARRIVED),
        (STARTED, STARTED),
        (IN_PROGRESS, IN_PROGRESS),
        (COMPLETED, COMPLETED),
        (PICKED_UP, PICKED_UP)
    )
    TIME_CAP = (
        (HOURS, HOURS),
        (DAYS, DAYS),
        (MONTHS, MONTHS),
    )
    RATINGS = (
        (1, 1),
        (2, 2),
        (3, 3),
        (4,4),
        (5,5)
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    state_within = models.CharField(max_length=100, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    subtype = models.ForeignKey(Subtype, on_delete=models.SET_NULL, null=True, blank=True)
    pick_up_address = models.CharField(max_length=255, null=True, blank=True)
    pick_up_lat = models.DecimalField(max_digits=30, decimal_places=15, null=True, blank=True)
    pick_up_long = models.DecimalField(max_digits=30, decimal_places=15, null=True, blank=True)
    drop_off_address = models.CharField(max_length=255, null=True, blank=True)
    drop_off_lat = models.DecimalField(max_digits=30, decimal_places=15, null=True, blank=True)
    drop_off_long = models.DecimalField(max_digits=30, decimal_places=15, null=True, blank=True)
    recipient_contact = PhoneNumberField(null=True, blank=True)
    sender_contact = PhoneNumberField(null=True, blank=True)
    item_description = models.TextField(null=True, blank=True)
    grocery_list = models.TextField(blank=True, null=True)
    grocery_estimated_price = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    describe_errand = models.TextField(null=True, blank=True)
    how_long = models.PositiveIntegerField(null=True, blank=True)
    time_cap = models.CharField(max_length=100, null=True, blank=True, choices=TIME_CAP)
    due_date = models.DateTimeField(blank=True, null=True)
    files = models.ManyToManyField(File, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUSES, default=REQUESTED)
    user_cancelled = models.BooleanField(default=False)
    estimated_pick_up_time = models.CharField(max_length=200, null=True, blank=True)
    estimated_drop_off_time = models.CharField(max_length=200, null=True, blank=True)
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
    agent_rating = models.CharField(max_length=100, null=True, blank=True, choices=RATINGS)


    def __str__(self):
        return f'{self.id}'

    def get_absolute_url(self):
        return reverse('errand:errand_detail', kwargs={'errand_id': self.id})

class OrderedMessagesManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().order_by('-timestamp')

class Conversation(models.Model):
    errand = models.ForeignKey(ErrandTask, on_delete=models.CASCADE, unique=True)
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="convo_customer"
    )
    agent = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="convo_agent"
    )
    start_time = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()
    ordered_messages = OrderedMessagesManager()

    @property
    def ordered_messages(self):
        return self.message_set.order_by('-timestamp')


class Message(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                              null=True, related_name='message_sender')
    text = models.CharField(max_length=200, blank=True)
    attachment = models.FileField(blank=True)
    conversation_id = models.ForeignKey(Conversation, on_delete=models.CASCADE,)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('timestamp',)

class Wallet(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Wallet for {self.user.email}"

class Earnings(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Earnings for {self.wallet.user.email} - {self.amount}"

class Withdrawals(models.Model):
    bank_name = models.CharField(max_length=200)
    bank_account_number = models.PositiveIntegerField()
    beneficiary_name = models.CharField(max_length=200)
    wallet = models.ForeignKey(Wallet, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Withdrawal for {self.wallet.user.email} - {self.amount}"



@receiver(post_save, sender=Earnings)
def update_wallet_balance(sender, instance, created, **kwargs):
    if created:
        wallet = instance.wallet
        wallet.balance += instance.amount
        wallet.save()

@receiver(post_save, sender=Withdrawals)
def update_wallet_balance(sender, instance, created, **kwargs):
    if created:
        wallet = instance.wallet
        wallet.balance += instance.amount
        wallet.save()
