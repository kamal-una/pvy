from django.db import models
from django.contrib.auth.models import User
from history.models import HistoricalRecords
from django.contrib.sessions.models import Session


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


class Patron(models.Model):
    title = models.CharField(max_length=10)
    first_name = models.CharField(max_length=40)
    last_name = models.CharField(max_length=40)
    address1 = models.CharField(max_length=50)
    address2 = models.CharField(max_length=50, blank=True)
    address3 = models.CharField(max_length=50, blank=True)
    city = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    post_code = models.CharField(max_length=50)
    email = models.EmailField()
    dob = models.DateField()
    created = models.DateField(auto_now_add=True)
    last_update = models.DateField(auto_now=True)
    password = models.CharField(max_length=128)
    friends = models.ManyToManyField('self', blank=True)

    def __unicode__(self):
        return u'%s %s' % (self.first_name, self.last_name)


class Patron_Phone(models.Model):
    type = models.CharField(max_length=30)
    number = models.CharField(max_length=30)
    patron = models.ForeignKey(Patron)

    def __unicode__(self):
        return self.type

    class Meta:
        ordering = ['type']


class Event(models.Model):
    year = models.IntegerField()
    event = models.CharField(max_length=100)
    description = models.TextField()
    created = models.DateField(auto_now_add=True)
    last_update = models.DateField(auto_now=True)

    def __unicode__(self):
        return self.event

    class Meta:
        ordering = ['year', 'event']


class Package(models.Model):
    package = models.CharField(max_length=100)
    description = models.TextField()

    def __unicode__(self):
        return self.package


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
    user = models.ForeignKey(User, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)

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
    year = models.IntegerField()
    performance = models.CharField(max_length=100)
    description = models.TextField()
    date = models.DateField()
    created = models.DateField(auto_now_add=True)
    last_update = models.DateField(auto_now=True)
    event = models.ForeignKey(Event)
    facility = models.ForeignKey(Facility)
    user = models.ForeignKey(User)
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
        return str(self.year) + " - " + self.performance

    class Meta:
        ordering = ['year', 'performance']


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
    patron = models.ForeignKey(Patron, null=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    payment_amount = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    package = models.ForeignKey(Package, null=True)

    history = HistoricalRecords()

    def lock_seat(self, user, buyer, price):
        # make a new transaction
        transaction = Transaction(user=user)
        transaction.save()

        # mark the seat as locked
        self.transaction = transaction
        self.status = Seat.LOCKED
        self.buyer_type = buyer
        self.price = price
        self.save()
        return self

    def unlock_seat(self, user):
        # make a new transaction
        transaction = Transaction(user=user)
        transaction.save()

        self.transaction = transaction
        self.status = Seat.AVAILABLE
        self.buyer_type = None
        self.price = 0
        self.save()

    def pay_seat(self, user):
        # make a new transaction
        transaction = Transaction(user=user)
        transaction.save()

        self.transaction = transaction
        self.status = Seat.PAID
        self.save()


    def __unicode__(self):
        return str(self.performance) + " - " + str(self.transaction) + " - " + str(self.seat)

    class Meta:
        ordering = ['performance', 'transaction', 'seat']


def getSeatCount(year, performance):
    seats_count = Seat.objects.filter(performance__year__exact=year, performance__performance__exact=performance).filter(status=0).count()
    return seats_count


def getPerformance(year, performance):
    performance = Performance.objects.get(year__exact=year, performance__exact=performance, publish__exact=True)
    return performance


def getPrices(performance):
    buyer = BuyerType.objects.filter(performance=performance.pk)
    prices = Price.objects.filter(price_map__exact=performance.price_map).filter(buyer_type=buyer).select_related('buyer_type')
    return prices


def getPerformances():
    return Performance.objects.filter(publish__exact=True)