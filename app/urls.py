from django.conf.urls import url
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # These are for user/page on our own
    url(r'^$', views.index, name='index'),
    #url(r'^login/$', views.login, name='login'),
    #url(r'^logout/$', views.logout, name='logout'),    
    # confirm email
    # change password
    # forgot passsword
    url(r'^login/$',
        auth_views.LoginView.as_view(template_name='registration/login.html'),
        name='login'),
    url(r'^logout/$', 
        auth_views.LogoutView.as_view(template_name='registration/logged_out.html'),
        name='logout'),
    url(r'^forgotpw', 
        auth_views.PasswordResetView.as_view(template_name='registration/page-forgot-password.html'),
        name='forgotpw'),                  
    url(r'password_reset_confirm/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$', 
        auth_views.PasswordResetConfirmView.as_view(template_name='registration/page-password_reset_confirm.html'),
        name='password_reset_confirm'),
    url(r'password_reset_complete',
        auth_views.PasswordResetDoneView.as_view(template_name='registration/page-password_reset_complete.html'),
        name='password_reset_complete'),        
    url(r'password_reset_done', 
        auth_views.PasswordResetDoneView.as_view(template_name='registration/page-password_reset_done.html'),
        name='password_reset_done'),
    
    url(r'^register/$', views.register, name='register'),
    url(r'^subscription/$', views.register, name='subscription'),
    url(r'^profile/$', views.register, name='profile'),
    
    
    # these stuff will be for account on linkedIN
    url(r'^accounts/settings/(?P<pk>[\d+])$', views.account, name='account-settings'),
    url(r'^accounts/add/$', views.update_account, name='add-account'),
    url(r'^accounts/remove/(?P<pk>[\d+])$', views.update_account, name='add-account'),
    url(r'^accounts/pinverify/(?P<pk>[\d+])$', views.update_account, name='pinverify'),
    
]
