from django.contrib import admin
from ticketing.models import System, CustomUser, Performance, PaymentType, BuyerType, Transaction, Seat, \
    Facility, SeatedFacilitySeat, Price, PriceMap


class PerformanceAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        obj.user = request.user
        obj.save()
    fields = ('performance', 'description', 'date', 'facility', 'buyer_types',
              'sale_start', 'sale_end', 'price_map', 'publish')
    list_display = ('performance', 'description', 'date', 'facility', 'created', 'last_update',
                    'sale_start', 'sale_end', 'price_map', 'publish')
    search_fields = ('performance', 'description')
    list_filter = ('date', 'created', 'last_update')


class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'title', 'first_name', 'last_name', 'date_joined', 'last_update')
    search_fields = ('first_name', 'last_name', 'email')
    list_filter = ('date_joined', 'last_update')


class BuyerAdmin(admin.ModelAdmin):
    list_display = ('buyer_type', 'description')
    search_fields = ('buyer_type', 'description')


class FacilityAdmin(admin.ModelAdmin):
    list_display = ('facility', 'seated', 'number_of_seats', 'created', 'last_update')
    search_fields = ('facility',)
    list_filter = ('created', 'last_update')


class PaymentTypeAdmin(admin.ModelAdmin):
    list_display = ('payment_type', 'description')
    search_fields = ('payment_type', 'description')


class SeatAdmin(admin.ModelAdmin):
    list_display = ('id', 'seat', 'performance', 'status', 'transaction', 'buyer_type', 'payment_type', 'user')
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
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Performance, PerformanceAdmin)
admin.site.register(PaymentType, PaymentTypeAdmin)
admin.site.register(BuyerType, BuyerAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Seat, SeatAdmin)
admin.site.register(Facility, FacilityAdmin)
admin.site.register(SeatedFacilitySeat, SeatedFacilitySeatAdmin)
admin.site.register(Price, PriceAdmin)
admin.site.register(PriceMap, PriceMapAdmin)
