from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns(
    '',
    url(r'^$', 'ticketing.views.buy'),
    url(r'^buy/$', 'ticketing.views.buy', name='buy'),
    url(r'^buy/(?P<year>\d{4})/(?P<performance>\w+)/$', 'ticketing.views.buy_perf', name='buy_perf'),

    url(r'^cart/$', 'ticketing.views.get_cart', name='cart'),
    url(r'^empty_cart/$', 'ticketing.views.empty_cart', name='empty_cart'),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
