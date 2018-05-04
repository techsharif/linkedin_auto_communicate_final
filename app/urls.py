from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^login/$', views.login, name='login'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^pinverify/$', views.pinverify, name='pinverify'),
    url(r'^account-settings/$', views.account, name='account-settings'),
    url(r'^save-account/$', views.save_account, name='save-account'),
    url(r'^register/$', views.register, name='register'),
]
