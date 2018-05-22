from django.conf.urls import url

#settings

from .views import DashBoard, Proxy


urlpatterns = [
    url(r'botstatus/(?P<pk>(\d+))', Proxy.as_view(), name='bot-status'),
    url(r'botlog/(?P<pk>(\d+))', Proxy.as_view(), name='bot-log'),
    url(r'^', DashBoard.as_view(), name='dashboard'),
    
]
