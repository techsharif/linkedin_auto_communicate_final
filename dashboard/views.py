import json

from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponse
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView
from django.views.generic.list import ListView
import requests

from app.models import LinkedInUser


#from django.shortcuts import render
login_decorators = (login_required, )

@method_decorator(login_decorators, name="dispatch")
class DashBoard(ListView):
    template_name = 'dashboard/home.html'
    model = LinkedInUser
    
    def get_queryset(self):
        qs = super(DashBoard, self).get_queryset()
        return qs

    def post(self, request):
        print(request.POST)
        id_ = request.POST['id']
        ip = request.POST['ip']

        linkedin_user = LinkedInUser.objects.get(id=id_)
        linkedin_user.bot_ip = ip
        linkedin_user.save()
        return redirect('dashboard')
    
    
    
class Proxy(TemplateView):
    def get_context_data(self, **kwargs):
        ctx = super(Proxy, self).get_context_data()
        print('path:', self.kwargs)
        linkedin  = LinkedInUser.objects.get(pk=self.kwargs.get('pk'))
        ip = linkedin.bot_ip
        rpath = '/'
        if 'log' in self.request.path:
            rpath = '/logs/'
            
        url = 'http://{ip}:8080{path}'.format(ip=ip, path=rpath)
        print('rurl:', url)
        res = requests.get(url) 
               
        ctx['data'] = res.json()
        
        #print('context:', ctx)
        return ctx
        
    def render_to_response(self, context, **response_kwargs):
        json_data = json.dumps(context['data'])
        return HttpResponse(json_data, content_type='application/json')
