import json

from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView
from django.views.generic.list import ListView
import requests

from app.models import LinkedInUser


# from django.shortcuts import render
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
        linkedin = LinkedInUser.objects.get(pk=self.kwargs.get('pk'))
        ip = linkedin.bot_ip
        rpath = '/'
        if 'log' in self.request.path:
            rpath = '/logs/'
        url = 'http://{ip}:8080{path}'.format(ip=ip, path=rpath)
        print('rurl:', url)
        res = requests.get(url)
        ctx['data'] = res.json()
        # print('context:', ctx)
        return ctx

    def get_linkedin_user_list(request):
        send_data = []
        try:
            user = request.user
            linkedin_user = LinkedInUser.objects.filter(user_id=user)
            print(linkedin_user)
            index = 0
            for linked_user in linkedin_user:
                action = ''
                activate = ''
                if linked_user.login_status:
                    action = '<button class="btn btn-sm btn-primary btn-gradient waves-effect waves-light activat-button" onclick="setting('+str(linked_user.id)+')">setting</button>'
                    action += '<button class="btn btn-sm btn-danger btn-gradient waves-effect waves-light activat-button" onclick="update_status('+str(linked_user.id)+', 0)">Off</button>'
                    activate = '''<button class="btn btn-sm btn-primary btn-gradient
                     waves-effect waves-light activat-button">active</button>'''
                else:
                    action = '<button class="btn btn-sm btn-primary btn-gradient waves-effect waves-light activat-button" onclick="update_status('+str(linked_user.id)+', 1)">On</button>'
                    activate = '<button class="btn btn-sm btn-danger btn-gradient waves-effect waves-light activat-button" >inactive</button>'
                if linked_user.bot_ip:
                    pass
                else:
                    action = '<button class="btn btn-sm btn-primary btn-gradient waves-effect waves-light activat-button" onclick="add_ip('+str(linked_user.id)+', 1)">Add Ip</button>'
                index += 1
                send_data.append({
                    'user': linked_user.id,
                    'email': linked_user.email,
                    'activate': activate,
                    'status': activate,
                    'action': action,
                    'bot_ip': linked_user.bot_ip,
                    'index': index
                })
        except LinkedInUser.DoesNotExist:
            send_data = []
        data = {'data': send_data}
        return JsonResponse(data)

    def update_status(request):
        message = ''
        response_code = 0
        try:
            if request.POST.get('linked_id'):
                linked_user = LinkedInUser.objects.filter(id=int(request.POST.get('linked_id')))
                linked_user.update(login_status=int(request.POST.get('status')))
                print(int(request.POST.get('linked_id')))
                if int(request.POST.get('status')) == 1:
                    message = 'Activated Successfully!'
                else:
                    message = 'Disactivated successfully!'
                response_code = 1
            else:
                message = 'Join error!'
        except LinkedInUser.DoesNotExist:
            message = 'Update error!'
        return JsonResponse({'message': message, 'response_code': response_code, 'data': '' })

    def update_ip(request):
        message = ''
        response_code = 0
        try:
            if request.POST.get('linked_id'):
                linked_user = LinkedInUser.objects.filter(id=int(request.POST.get('linked_id')))
                linked_user.update(bot_ip=str(request.POST.get('ip')))
                message = 'Add Ip successfully!'
                response_code = 1
            else:
                message = 'Update error!'
        except LinkedInUser.DoesNotExist:
            message = 'Update error!'
        return JsonResponse({'message': message, 'response_code': response_code})

    def render_to_response(self, context, **response_kwargs):
        json_data = json.dumps(context['data'])
        return HttpResponse(json_data, content_type='application/json')
