from django.conf.urls import url
from messenger import views

urlpatterns = [
    url(r'^messenger/$', views.messenger_home, name='messenger_home'),
    url(r'^campaigns/$', views.campaigns, name='campaigns'),
    url(r'^campaigns/(?P<campaign_id>\d+)/$', views.getcampaigns, name='get_campaigns'),
]
