from django.conf.urls import url

# settings

from .views import DashBoard, Proxy


urlpatterns = [
    url(r'botstatus/(?P<pk>(\d+))', Proxy.as_view(), name='bot-status'),
    url(r'botlog/(?P<pk>(\d+))', Proxy.as_view(), name='bot-log'),
    url(r'^$', DashBoard.as_view(), name='dashboard'),
    url(r'update_status', Proxy.update_status, name='updateStatus'),
    url(r'update_ip', Proxy.update_ip, name='updateIp'),
    url(r'getaccountlist/', Proxy.get_linkedin_user_list, name='get_linked_list')
]
