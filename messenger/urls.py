from django.conf.urls import url
from messenger import views

urlpatterns = [
    #url(r'^messenger/$', views.messenger_home, name='messenger_home'),
    #url(r'^campaigns/$', views.campaigns, name='campaigns'),
    #url(r'^campaigns/(?P<campaign_id>\d+)/$', views.getcampaigns, name='get_campaigns'),
    #url(r'^delete_campaigns/(?P<campaign_id>\d+)/$', views.delete_campaigns, name='delete_campaigns'),
    #url(r'^update_campaigns/(?P<campaign_id>\d+)/$', views.update_campaigns, name='update_campaigns'),
    
    url(r'^campaign/contacts/', views.CampaignContactsView.as_view(),
        name='campaign-contacts')
]
