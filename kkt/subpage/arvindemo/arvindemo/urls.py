from django.conf.urls import patterns, include, url
from views import *
from django.conf import settings
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
# admin.autodiscover()

handler500 = 'server_error'
urlpatterns = patterns('',
    url(r'^hello/$', hello),  # hello world
	url(r'^$', homePage),
	url(r'^time/$', getTime),
    url(r'^time/plus/(\d{1,2})/$', hoursAhead),
	url(r'^Ttime/$', templateGetTime),
	url(r'^Mall$', templateMall),
	url(r'^Contest$', templateContest),
    url(r'^Presentation$', templatePresentation),
    url(r'^Habit$', templateHabit),
    url(r'^Weather$', templateWeather),
    url(r'^Help$', helpPage),
    url(r'^404$', page404),
    url(r'^500$', server_error),
    url(r'^submitPage$', submitPage),
    url(r'^submitMall$', submitMall),
    url(r'^submitContest$', submitContest),
    url(r'^submitPresentation$', submitPresentation),
    url(r'^submitHabit$', submitHabit),
    url(r'^submitWeather$', submitWeather),
    url(r'^terms$', terms),
    url(r'^privacy$', privacy),
    url(r'^thanks$', thanks),
    url(r'^about$', about),
    url(r'^qa$', qa),
    url(r'^static/(?P<path>.*)$','django.views.static.serve',{'document_root':settings.STATICFILES_DIRS}),
    # Examples:
    # url(r'^$', 'arvindemo.views.home', name='home'),
    # url(r'^arvindemo/', include('arvindemo.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    #url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    #url(r'^admin/', include(admin.site.urls)),
)
