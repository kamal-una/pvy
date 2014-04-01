from django.db import models
from django.contrib.auth.models import User
from history.models import HistoricalRecords
from django.contrib.sessions.models import Session
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.core.mail import send_mail
from django.utils.http import urlquote
from django.contrib.auth.models import BaseUserManager


class System(models.Model):
    name = models.CharField(max_length=100)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Facility(models.Model):
    facility = models.CharField(max_length=100)
    seated = models.BooleanField()
    number_of_seats = models.BigIntegerField(null=True)
    created = models.DateField(auto_now_add=True)
    last_update = models.DateField(auto_now=True)

    def save(self, *args, **kwargs):
        # if new performance
        if self.pk:
            # delete all the SeatedFacilitySeat records
            SeatedFacilitySeat.objects.filter(facility=self).delete()

        # save the facility...
        super(Facility, self).save(*args, **kwargs)

        # create the facility seats...
        for i in range(1, self.number_of_seats + 1):
            new_seat_record = SeatedFacilitySeat(facility=self, section='GA', row='', seat=i)
            new_seat_record.save()

    def __unicode__(self):
        return self.facility


class SeatedFacilitySeat(models.Model):
    facility = models.ForeignKey(Facility)
    section = models.CharField(max_length=10)
    row = models.CharField(max_length=10)
    seat = models.IntegerField()

    def __unicode__(self):
        return self.section + " - " + self.row + " - " + str(self.seat)


class CustomUserManager(BaseUserManager):

    def _create_user(self, email, password,
                     is_staff, is_superuser, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        now = timezone.now()
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email,
                          is_staff=is_staff, is_active=True,
                          is_superuser=is_superuser, last_login=now,
                          date_joined=now, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        return self._create_user(email, password, False, False,
                                 **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        return self._create_user(email, password, True, True,
                                 **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    title = models.CharField(max_length=10, blank=True)
    first_name = models.CharField(max_length=40, blank=True)
    last_name = models.CharField(max_length=40, blank=True)
    address1 = models.CharField(max_length=50, blank=True)
    address2 = models.CharField(max_length=50, blank=True)
    address3 = models.CharField(max_length=50, blank=True)
    city = models.CharField(max_length=50, blank=True)
    country = models.CharField(max_length=50, blank=True)
    post_code = models.CharField(max_length=50, blank=True)

    dob = models.DateField(null=True, blank=True)
    last_update = models.DateField(auto_now=True)
    friends = models.ManyToManyField('self', blank=True)

    is_staff = models.BooleanField(_('staff status'), default=False,
        help_text=_('Designates whether the user can log into this admin site.'))
    is_active = models.BooleanField(_('active'), default=True,
        help_text=_('Designates whether this user should be treated as active. Unselect this instead of deleting accounts.'))
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def get_absolute_url(self):
        return "/users/%s/" % urlquote(self.email)

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """
        Returns the short name for the user.
        """
        return self.first_name

    def email_user(self, subject, message, from_email=None):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email])


class Patron_Phone(models.Model):
    type = models.CharField(max_length=30)
    number = models.CharField(max_length=30)
    patron = models.ForeignKey(CustomUser)

    def __unicode__(self):
        return self.type

    class Meta:
        ordering = ['type']


class BuyerType(models.Model):
    buyer_type = models.CharField(max_length=100)
    description = models.TextField()

    def __unicode__(self):
        return self.buyer_type


class PaymentType(models.Model):
    payment_type = models.CharField(max_length=100)
    description = models.TextField()

    def __unicode__(self):
        return self.payment_type


class Transaction(models.Model):
    user = models.ForeignKey(CustomUser, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    def create(self, user):
        transaction = Transaction(user=user)
        transaction.save()
        return transaction

    def __unicode__(self):
        return str(self.id)


class PriceMap(models.Model):
    price_map = models.CharField(max_length=100)
    description = models.TextField()

    def __unicode__(self):
        return str(self.price_map)


class Price(models.Model):
    price_map = models.ForeignKey(PriceMap, null=False)
    buyer_type = models.ForeignKey(BuyerType)
    price = models.DecimalField(max_digits=8, decimal_places=2)

    def __unicode__(self):
        return "%s - %s - %s " % (str(self.price_map), str(self.buyer_type), str(self.price))


class Performance(models.Model):
    performance = models.CharField(max_length=100)
    description = models.TextField()
    date = models.DateField()
    created = models.DateField(auto_now_add=True)
    last_update = models.DateField(auto_now=True)
    facility = models.ForeignKey(Facility)
    user = models.ForeignKey(CustomUser)
    buyer_types = models.ManyToManyField(BuyerType, blank=True)
    sale_start = models.DateTimeField(blank=True, null=True)
    sale_end = models.DateTimeField(blank=True, null=True)
    price_map = models.ForeignKey(PriceMap)
    publish = models.BooleanField()

    def save(self, *args, **kwargs):
        # save the performance...
        if self.pk is None:
            do_seats = True
        else:
            do_seats = False

        super(Performance, self).save(*args, **kwargs)

        # if new performance
        if do_seats:
            # a new transaction for creating these seats...
            new_transaction = Transaction(user=self.user)
            new_transaction.save()

            # create the seats...
            all_seats = SeatedFacilitySeat.objects.filter(facility__facility__exact=self.facility)
            for new_seat in all_seats:
                new_seat_record = Seat(seat=new_seat, status=0, transaction=new_transaction, performance=self, price=0)
                new_seat_record.save()

    def lock_seat(self, user, buyer, price):
        # find an available seat...
        seat = self.seat_set.filter(status=0).first()
        if seat:
            seat = seat.lock_seat(user, buyer, price)
            return seat

        return None

    def __unicode__(self):
        return self.performance

    class Meta:
        ordering = ['performance']


class Seat(models.Model):
    AVAILABLE = 0
    LOCKED = 1
    UNPAID = 2
    CONSIGNED = 3
    PAID = 4
    PRINTED = 5
    STATUS_CHOICES = (
        (AVAILABLE, 'Available'),
        (LOCKED, 'Locked'),
        (UNPAID, 'Unpaid'),
        (CONSIGNED, 'Consigned'),
        (PAID, 'Paid'),
        (PRINTED, 'Printed'),
    )

    transaction = models.ForeignKey(Transaction)
    performance = models.ForeignKey(Performance)
    seat = models.ForeignKey(SeatedFacilitySeat, related_name='+')
    status = models.IntegerField(choices=STATUS_CHOICES, default=AVAILABLE)
    buyer_type = models.ForeignKey(BuyerType, null=True)
    payment_type = models.ForeignKey(PaymentType, null=True)
    user = models.ForeignKey(CustomUser, null=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    payment_amount = models.DecimalField(max_digits=8, decimal_places=2, null=True)

    history = HistoricalRecords()

    def lock_seat(self, transaction, buyer, price):
        self.buyer_type = buyer
        self.price = price
        self.update_seat(transaction, Seat.LOCKED)
        return self

    def unlock_seat(self, transaction):
        self.buyer_type = None
        self.price = 0
        self.update_seat(transaction, Seat.AVAILABLE)

    def pay_seat(self, transaction, user):
        self.user = user
        self.update_seat(transaction, Seat.PAID)


    def update_seat(self, transaction, status):
        self.transaction = transaction
        self.status = status
        self.save()

    def __unicode__(self):
        return str(self.performance) + " - " + str(self.transaction) + " - " + str(self.seat)

    class Meta:
        ordering = ['performance', 'transaction', 'seat']


def get_seat_count(performance):
    seats_count = Seat.objects.filter(performance__performance__exact=performance).filter(status=0).count()
    return seats_count


def get_performance(performance):
    performance = Performance.objects.get(performance__exact=performance, publish__exact=True)
    return performance


def get_prices(performance):
    buyer = BuyerType.objects.filter(performance=performance.pk)
    prices = Price.objects.filter(price_map__exact=performance.price_map).filter(buyer_type=buyer).select_related('buyer_type')
    return prices


def get_performances():
    return Performance.objects.filter(publish__exact=True)


def create_transaction(user):
    if user.is_authenticated():
        transaction = Transaction(user=user)
    else:
        transaction = Transaction()
    transaction.save()
    return transaction