from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns(
    'ticketing.views',
    url(r'^$', 'buy'),
    url(r'^buy/$', 'buy', name='buy'),
    url(r'^buy/(?P<performance>[-\w\ ]+)/$', 'buy_perf', name='buy_perf'),

    url(r'^cart/$', 'get_cart', name='cart'),
    url(r'^empty_cart/$', 'empty_cart', name='empty_cart'),
    url(r'^purchase/$', 'purchase', name='purchase'),
    url(r'^confirm/$', 'confirm', name='confirm'),
    url(r'^register/$', 'register', name='register'),
    url(r'^account/$', 'account', name='account'),
    url(r'^logout/$', 'user_logout', name='logout'),
    url(r'^refund_seat/(?P<seat>\w+)/$', 'refund_seat', name='refund_seat'),
)

urlpatterns += patterns(
    'reporting.views',
    url(r'^report/$', 'report', name='report'),
    url(r'^report/(?P<performance>[-\w\ ]+)/$', 'report_perf', name='report_perf'),
)

urlpatterns += patterns(
    'django.contrib.auth.views',
    url(r'^login/$', 'login', {'template_name': 'login.html'}, name='login'),
)

urlpatterns += patterns(
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
)