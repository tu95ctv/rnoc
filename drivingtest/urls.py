from django.contrib.auth.forms import AdminPasswordChangeForm
import django.contrib.auth.urls
print 'in url 3'
from django.conf.urls import patterns, url, include
from drivingtest import views
from django.conf import settings
from django.contrib import admin

# UNDERNEATH your urlpatterns definition, add the following two lines:
admin.autodiscover()
urlpatterns = patterns('',
        
        #################OMCKV2####################
        url(r'^omckv$', views.omckv2, name='index'),
        url(r'^omckv2/tram_table/$',  views.tram_table, name='tram_table'),
        url(r'^omckv2/suggestion/$', views.suggestion, name='suggestion'),
        url(r'^omckv2/lenh-suggestion/$', views.lenh_suggestion, name='suggestion'),
        url(r'^omckv2/upload_excel_file/$', views.upload_excel_file, name='upload_file'),
        url(r'^omckv2/search_history/$', views.search_history, name='suggestion'),
        url(r'^omckv2/edit_history_search/$', views.edit_history_search, name='suggestion'),
        url(r'^omckv2/modelmanager/(?P<form_name>\w+)/(?P<entry_id>\w+)/$', views.modelmanager, name='suggestion'),
        url(r'^omckv2/managertable/(?P<table_name>\w+)/$',views.modelmanager,name="managertable"),
        url(r'^omckv2/$',  views.omckv2, name='omckv2'),
        url(r'^omckv2/download-script/$',  views.download_script, name='omckv2'),
        url(r'^omckv2/delete_mll/$',  views.delete_mll, name='tram_table'),
        url(r'^omckv2/autocomplete/$',  views.autocomplete, name='tram_table'),
        url(r'^omckv2/download_script_ntp/$',  views.download_script_ntp, name='tram_table'),
        
       
        url(r'^accounts/', include('django.contrib.auth.urls')),
        
        
        
        #######FORUM
        
        
        
        url(r'^$', views.index, name='index'),
        url(r'^select_forum/$',  views.select_forum, name='select_forum'),
        url(r'^get-thongbao/$',  views.get_thongbao, name='get-thongbao'),
        url(r'^leech/$',  views.leech, name='leech'),
        url(r'^importul/$',  views.importul, name='importul'),
        url(r'^stop-post/$',  views.stop_post, name='stop-post'),
        url(r'^get_description/$',  views.get_description, name='tao-object'),
        url(r'^edit_entry/(?P<entry_id>\d+)/$',  views.edit_entry, name='edit_entry'),
        
        
        ##########CHUNG
        #url(r'^$', views.index, name='index'),
        url(r'^login/$',views.user_login,name="user_login"),
        url(r'^logout/$',views.user_logout,name="user_logout"),
        url(r'^omckv2/registers/$', views.register, name='register'), # ADD NEW PATTERN! 
                   
        )
if settings.DEBUG:
    urlpatterns += patterns( 
        'django.views.static',
        (r'media/(?P<path>.*)',
        'serve',
        {'document_root': settings.MEDIA_ROOT}), )
 
    
    
    