from django.contrib import admin
from ticketing.models import System, Patron, Event, Performance, PaymentType, BuyerType, Package, Transaction, Seat, \
    Facility, SeatedFacilitySeat, Price, PriceMap


class PerformanceAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        obj.user = request.user
        obj.save()
    fields = ('year', 'performance', 'description', 'date', 'event', 'facility', 'buyer_types',
              'sale_start', 'sale_end', 'price_map', 'publish')
    list_display = ('performance', 'year', 'description', 'date', 'event', 'facility', 'created', 'last_update',
                    'sale_start', 'sale_end', 'price_map', 'publish')
    search_fields = ('year', 'performance', 'description', 'event__event')
    list_filter = ('date', 'created', 'last_update')


class PatronAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'first_name', 'last_name', 'email', 'created', 'last_update')
    search_fields = ('first_name', 'last_name', 'email')
    list_filter = ('created', 'last_update')


class BuyerAdmin(admin.ModelAdmin):
    list_display = ('buyer_type', 'description')
    search_fields = ('buyer_type', 'description')


class EventAdmin(admin.ModelAdmin):
    list_display = ('year', 'event', 'description', 'created', 'last_update')
    search_fields = ('year', 'event', 'description')
    list_filter = ('created', 'last_update')


class FacilityAdmin(admin.ModelAdmin):
    list_display = ('facility', 'seated', 'number_of_seats', 'created', 'last_update')
    search_fields = ('facility',)
    list_filter = ('created', 'last_update')


class PaymentTypeAdmin(admin.ModelAdmin):
    list_display = ('payment_type', 'description')
    search_fields = ('payment_type', 'description')


class SeatAdmin(admin.ModelAdmin):
    list_display = ('id', 'seat', 'performance', 'status', 'transaction', 'buyer_type', 'payment_type', 'patron')
    search_fields = ('id', 'seat__section', 'seat__row', 'seat__seat', 'status')


class SeatedFacilitySeatAdmin(admin.ModelAdmin):
    list_display = ('id', 'facility', 'section', 'row', 'seat')
    search_fields = ('facility', 'section', 'row', 'seat')


class TransactionAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        obj.user = request.user
        obj.save()

    list_display = ('id', 'date', 'user')
    search_fields = ('id', 'date', 'user')
    list_filter = ('date',)


class PriceAdmin(admin.ModelAdmin):
    list_display = ('price_map', 'buyer_type', 'price')
    search_fields = ('price_map', 'buyer_type', 'price')
    list_filter = ['price_map']


class PriceMapAdmin(admin.ModelAdmin):
    list_display = ('price_map',)
    search_fields = ('price_map',)

admin.site.register(System)
admin.site.register(Patron, PatronAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(Performance, PerformanceAdmin)
admin.site.register(PaymentType, PaymentTypeAdmin)
admin.site.register(BuyerType, BuyerAdmin)
admin.site.register(Package)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Seat, SeatAdmin)
admin.site.register(Facility, FacilityAdmin)
admin.site.register(SeatedFacilitySeat, SeatedFacilitySeatAdmin)
admin.site.register(Price, PriceAdmin)
admin.site.register(PriceMap, PriceMapAdmin)
