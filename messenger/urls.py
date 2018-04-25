from django.conf.urls import url
from messenger import views

urlpatterns = [
    url(r'^$', views.messenger_home, name='messenger_home'),
]
