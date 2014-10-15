from django.conf.urls import patterns, include, url
#import settings module from django.conf to allow access of variables within settings.py
from django.conf import settings
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'tango_with_django_project.views.home', name='home'),
    # url(r'^tango_with_django_project/', include('tango_with_django_project.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    #mapping the rango apps urls to the master urls
    url(r'^rango/', include('rango.urls'))
)
#if running in DEBUG mode
if settings.DEBUG:
    #add a new pattern to the urlpatterns
    urlpatterns += patterns(
        #for every any file requested with the media url the request will be passed to django.views.static
        'django.views.static',
        (r'media/(?P<path>.*)',
        'serve',
         {'document_root': settings.MEDIA_ROOT}),
    )


