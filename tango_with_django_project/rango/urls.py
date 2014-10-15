from django.conf.urls import patterns, url
import views

#the first url() is the rango app itself. It contains an empty string regular expression. This is because rango is run first when entering ../rango
urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
                     #second url() is the rango/about/
    url(r'^about/', views.index2, name='index2'),
    url(r'^add_category/$', views.add_category, name='add_category'), # NEW MAPPING!
    url(r'^category/(?P<category_name_url>\w+)/add_page/$', views.add_page, name='page'),
    #third url() is the rango/category/<category name>
    url(r'^category/(?P<category_name_url>\w+)/$', views.category, name='category'),
    url(r'^register/$', views.register, name='register'),
    url(r'^login/$', views.user_login, name='login'),
    url(r'^restricted/', views.restricted, name='restricted'),
    url(r'^logout/$', views.user_logout, name='logout'),
    url(r'^search/$',views.search, name='search'),
    url(r'^profile/$', views.profile, name='profile'),
    url(r'^goto/$', views.track_url, name='track_url'),
    url(r'^like_category/$', views.like_category, name='like_category'),

    )