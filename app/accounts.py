import datetime
import json

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.db import transaction
from django.forms.models import model_to_dict
from django.http.response import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.template.loader import render_to_string
from django.urls.base import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import TemplateView, View
from django.views.generic.detail import DetailView, BaseDetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView

from app.models import LinkedInUser, Membership, BotTask, LinkedInUserAccountStatus

from checkuser.checkuser import exist_user
from connector.models import Search, TaskQueue
from messenger.forms import CreateCampaignForm, CreateCampaignMesgForm, \
    UpdateCampWelcomeForm, InlineCampaignStepFormSet, UpdateCampConnectForm
from messenger.models import Inbox, ContactStatus, Campaign

User = get_user_model()
decorators = (never_cache, login_required,)


@method_decorator(decorators, name='dispatch')
class AccountList(ListView):
    model = LinkedInUser
    queryset = LinkedInUser.objects.filter(status=LinkedInUserAccountStatus.DONE)


class AccountMixins(object):
    def get_context_data(self, **kwargs):
        ctx = super(AccountMixins, self).get_context_data(**kwargs)
        # pk here is pk of linkeduser table, 
        if 'object' in ctx:
            if isinstance(ctx['object'], Campaign):
                ctx['pk'] = ctx['object'].owner_id
            else:
                ctx['pk'] = ctx['object'].id
        else:
            ctx['pk'] = self.kwargs.get('pk')

        return ctx


@method_decorator(decorators, name='dispatch')
class AccountDetail(AccountMixins, DetailView):
    template_name = 'app/accounts_detail.html'
    model = LinkedInUser

    def get_context_data(self, **kwargs):
        ctx = super(AccountDetail, self).get_context_data(**kwargs)
        # count connection number by
        linkedIn_user = ctx['object']
        statuses = [ContactStatus.CONNECTED, ContactStatus.OLD_CONNECT]
        ctx['connection_count'] = Inbox.objects.filter(owner=linkedIn_user,
                                                       status__in=statuses).count()
        camp_qs = Campaign.objects.filter(owner=linkedIn_user)
        ctx['messengers'] = camp_qs.filter(is_bulk=True)
        ctx['connectors'] = camp_qs.filter(is_bulk=False)
        ctx['account_home'] = True

        return ctx


@method_decorator(decorators, name='dispatch')
class AccountSettings(UpdateView):
    model = LinkedInUser
    fields = ['start_from', 'start_to', 'is_weekendwork', 'tz']
    template_name = 'app/accounts_settings.html'

    def get_success_url(self):
        return reverse('account-settings', kwargs={'pk': self.object.pk})


csrf_exempt_decorators = decorators + (csrf_exempt,)
@method_decorator(csrf_exempt_decorators, name='dispatch')
class AccountAdd(View):
    def post(self, request):
        if 'email' in request.POST.keys() and 'password' in request.POST.keys():
            user_email = request.POST['email'].strip()
            user_password = request.POST['password'].strip()
            # # collect membership data of this user
            # membership = Membership.objects.get(user=request.user)
            #
            # # create of get linkedin user
            linkedin_user, created = LinkedInUser.objects.get_or_create(
                user=request.user, email=user_email,
                password=user_password)

            # linkedin_user.latest_login = datetime.datetime.now()
            linkedin_user.save()
            if created:
                BotTask(owner=linkedin_user, task_type='add account',
                    name='add linkedin account').save()

        return redirect('accounts')

@method_decorator(csrf_exempt_decorators, name='dispatch')
class AccountInfo(View):
    def post(self, request):
        print(request.POST)
        if 'email' in request.POST.keys() and 'password' in request.POST.keys():
            user_email = request.POST['email'].strip()
            user_password = request.POST['password'].strip()
            linkedin_user = LinkedInUser.objects.get(email=user_email,password=user_password)

            if linkedin_user.status == LinkedInUserAccountStatus.PIN_REQUIRED:
                return HttpResponse(render_to_string('app/pinverify.html',{'object':linkedin_user}))
            elif linkedin_user.status == LinkedInUserAccountStatus.PIN_INVALID:
                return HttpResponse(render_to_string('app/pinverify.html',{'object':linkedin_user, 'error':True}))
            elif linkedin_user.status == LinkedInUserAccountStatus.DONE :
                return HttpResponse('<script> window.location.href = "/accounts/"; </script>')
            elif linkedin_user.status == LinkedInUserAccountStatus.PIN_CHECKING :
                return HttpResponse('pin checking')
            else:
                return HttpResponse('Processing')
        if 'id' in request.POST.keys() and 'pin' in request.POST.keys():
            id_ = int(request.POST['id'].strip())

            pin = request.POST['pin'].strip()
            linkedin_user = LinkedInUser.objects.get(id=id_)
            linkedin_user.pin = pin
            linkedin_user.status = LinkedInUserAccountStatus.PIN_CHECKING
            linkedin_user.save()
            return HttpResponse('pin checking')


csrf_exempt_decorators = decorators + (csrf_exempt,)
@method_decorator(csrf_exempt_decorators, name='dispatch')
class AddPin(View):
    def post(self, request):
        if 'pin' in request.POST.keys():
            user_email = request.POST['email'].strip()
            user_password = request.POST['password'].strip()
            # collect membership data of this user
            membership = Membership.objects.get(user=request.user)

            # create of get linkedin user
            linkedin_user, created = LinkedInUser.objects.get_or_create(
                user=request.user, email=user_email,
                password=user_password)

            linkedin_user.latest_login = datetime.datetime.now()
            linkedin_user.save()
            linkedin_user.membership.add(membership)

            BotTask(owner=linkedin_user, task_type='add account',
                    name='add linkedin account').save()

        return redirect('accounts')


class DataTable(object):
    status = []
    model = Inbox
    
    def default(self, o):
        if type(o) is datetime.date or type(o) is datetime.datetime:
            return o.strftime("%d/%m/%Y @ %H:%M")
    
    def get_queryset(self):
        qs = super(DataTable, self).get_queryset()
        qs = qs.filter(owner_id=self.kwargs.get('pk'))
        
        # if 'my network' should limit 'connected' or 'old connected'
        if len(self.status) > 0:
            qs = qs.filter(status__in=self.status)
            
        if self.request.is_ajax():
            qs = qs.values_list('id', 'name', 'company', 'industry', 'title',
                          'location', 'latest_activity', 'status')
        return qs
    
    
    def get_context_data(self, **kwargs):
        ctx = super(DataTable, self).get_context_data(**kwargs)
        if self.request.is_ajax():
            return ctx
            
        
        ctx['object_list'] = []
        
        return ctx
    
    def render_to_response(self, context, **response_kwargs):
        if self.request.is_ajax():
            #data = serializers.serialize('json', context['object_list'])
            data = [list(x) for x in context['object_list']]
            print('data:', data)
                      
            json_data = json.dumps(dict(data=data), default=self.default)
            return HttpResponse(json_data, content_type='application/json')
            
        return super(DataTable, self).render_to_response(context, **response_kwargs)

@method_decorator(decorators, name='dispatch')
class AccountNetwork(AccountMixins, DataTable, ListView):
    template_name = 'app/accounts_network.html'
    status = [ContactStatus.CONNECTED, ContactStatus.OLD_CONNECT]


@method_decorator(decorators, name='dispatch')
class AccounMessenger(AccountMixins, ListView):
    template_name = 'app/accounts_messenger.html'
    is_bulk = True
    model = Campaign

    def get_queryset(self):
        qs = super(AccounMessenger, self).get_queryset()
        qs = qs.filter(is_bulk=self.is_bulk, owner_id=self.kwargs.get('pk'))
        return qs


@method_decorator(decorators, name='dispatch')
class AccountCampaign(AccounMessenger):
    template_name = 'app/accounts_campaign.html'
    is_bulk = False


@method_decorator(decorators, name='dispatch')
class AccountSearch(View):
    template_name = 'app/accounts_search.html'

    def get(self, request, pk):
        searches = Search.objects.filter(owner__pk=pk)
        return render(request, self.template_name,{'searches': searches, 'pk':pk})

    def post(self, request, pk):

        if 'add_new_search_item' in request.POST.keys():
            name = request.POST['name'].strip()
            keywords = request.POST['keywords'].strip()
            search = Search(search_name=name, keyword=keywords)
            search.save()
            TaskQueue(content_object=search).save()
        print(request.POST)
        searches = Search.objects.filter(owner__pk=pk)
        return render(request, self.template_name, {'searches': searches, 'pk':pk})


@method_decorator(decorators, name='dispatch')
class AccountInbox(AccountMixins, DataTable, ListView):
    template_name = 'app/accounts_inbox.html'
    

@method_decorator(decorators, name='dispatch')
class AccountTask(AccountMixins, TemplateView):
    template_name = 'app/accounts_task.html'


@method_decorator(decorators, name='dispatch')
class AccountMessengerCreate(AccountMixins, CreateView):
    template_name = 'app/accounts_messenger_add.html'
    form_class = CreateCampaignMesgForm
    is_bulk = True

    def get_form(self, form_class=None):

        acc_id = self.kwargs.get('pk')
        if self.request.method == "POST":
            form = self.form_class(self.request.POST, owner_id=acc_id,
                                   is_bulk=self.is_bulk)
        else:
            form = self.form_class(owner_id=acc_id, is_bulk=self.is_bulk)
        return form

    def get_success_url(self):

        return reverse_lazy('account-messenger', kwargs=self.kwargs)

    def form_invalid(self, form):
        print('form_invalid:', form.is_valid(), form)
        return super(AccountMessengerCreate, self).form_invalid(form)

    def form_valid(self, form):
        data = self.get_context_data()
        acc_id = self.kwargs.get('pk')
        print('data:', self.kwargs, data)
        if form.is_valid():
            camp = form.save(commit=False)
            camp.owner_id = acc_id
            camp.is_bulk = self.is_bulk
            camp.save()
            return super(AccountMessengerCreate, self).form_valid(form)

        return super(AccountMessengerCreate, self).form_invalid(form)

        camp = form.instance
        camp.owner_id = acc_id
        camp.is_bulk = self.is_bulk
        camp = form.save()
        # if copy step message
        if camp.copy_campaign:
            camp.copy_step_message()

        return super(AccountMessengerCreate, self).form_valid(form)


@method_decorator(decorators, name='dispatch')
class AccountCampaignCreate(AccountMessengerCreate):
    template_name = 'app/accounts_campaign_add.html'
    is_bulk = False

    form_class = CreateCampaignForm

    def __init__(self, *args, **kwargs):
        super(AccountCampaignCreate, self).__init__()
        self.is_bulk = False

    def get_success_url(self):
        return reverse_lazy('account-campaign', kwargs=self.kwargs)


@method_decorator(decorators, name='dispatch')
class AccountMessengerDelete(AccountMixins, DeleteView):
    model = Campaign

    def delete(self, request, *args, **kwargs):
        self.get_object().delete()
        payload = {'deleted': 'ok'}
        return JsonResponse(json.dumps(payload), safe=False)


@method_decorator(decorators, name='dispatch')
class AccountMessengerActive(View):
    def get(self, request, pk):

        row = get_object_or_404(Campaign, pk=pk)
        if "1" in self.request.GET.get('active'):
            row.status = True
        else:
            row.status = False

        row.save()
        payload = {'ok': row.status}
        return JsonResponse(json.dumps(payload), safe=False)


@method_decorator(decorators, name='dispatch')
class AccountMessengerDetail(AccountMixins, UpdateView):
    template_name = 'app/accounts_messenger_update.html'
    form_class = UpdateCampWelcomeForm
    model = Campaign

    def get_context_data(self, **kwargs):
        data = super(AccountMessengerDetail, self).get_context_data(**kwargs)
        row = data['object']
        print('row object:', row)
        if self.request.POST:
            data['campaignsteps'] = InlineCampaignStepFormSet(self.request.POST,
                                                              instance=row)
        else:
            data['campaignsteps'] = InlineCampaignStepFormSet(instance=row)
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        campaignsteps = context['campaignsteps']
        print('form_valid form:', form.is_valid(), form.errors)

        with transaction.atomic():
            self.object = form.save()
            print('campaignsteps:', campaignsteps.is_valid(), campaignsteps.errors)
            if campaignsteps.is_valid():
                campaignsteps.instance = self.object
                campaignsteps.save()
                print('campaignsteps:', campaignsteps)
                if self.request.is_ajax():
                    payload = {'ok': True}
                    return JsonResponse(json.dumps(payload), safe=False)
            else:

                if self.request.is_ajax():
                    payload = {'error': campaignsteps.errors}
                    return JsonResponse(json.dumps(payload), safe=False)

        return super(AccountMessengerDetail, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('messenger-campaign', kwargs=self.kwargs)

    def form_invalid(self, form):
        print('form invalid:', form.errors)
        return super(AccountMessengerDetail, self).form_invalid(form)


@method_decorator(decorators, name='dispatch')
class AccountCampaignDetail(AccountMessengerDetail):
    template_name = 'app/accounts_campaign_update.html'
    form_class = UpdateCampConnectForm


class JSONResponseMixin:
    """
    A mixin that can be used to render a JSON response.
    """

    def render_to_json_response(self, context, **response_kwargs):
        """
        Returns a JSON response, transforming 'context' to make the payload.
        """
        response_kwargs['safe'] = False
        return JsonResponse(
            self.get_data(context),
            **response_kwargs
        )

    def get_data(self, context):
        """
        Returns an object that will be serialized as JSON by json.dumps().
        """

        return context['object'].toJSON()


class JSONDetailView(JSONResponseMixin, BaseDetailView):
    def render_to_response(self, context, **response_kwargs):
        return self.render_to_json_response(context, **response_kwargs)


csrf_exempt_decorators = decorators + (csrf_exempt,)


@method_decorator(csrf_exempt_decorators, name='dispatch')
class AccountBotTask(JSONDetailView):
    template_name = 'app/bottask_detail.html'
    model = BotTask


def can_add_account(user):
    # check if the current user can add more linked account
    pass


def remove_account(request, pk):
    LinkedInUser.objects.get(id=pk).delete()
    return redirect('accounts')





@method_decorator(csrf_exempt_decorators, name='dispatch')
class SearchResultView(View):
    def post(self, request):
        print(request.POST)

        return render(request, 'app/seach_render/search_render.html')



@method_decorator(csrf_exempt_decorators, name='dispatch')
class SearchItemView(View):
    def post(self, request):
        print(request.POST)

        return render(request, 'app/seach_render/search_item_render.html')
