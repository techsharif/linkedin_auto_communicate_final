import datetime
import json

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.db import transaction
from django.forms.models import model_to_dict
from django.http.response import JsonResponse, HttpResponse, HttpResponseRedirect
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

from app.forms import SearchForm
from app.models import LinkedInUser, Membership, BotTask, BotTaskType, BotTaskStatus

from checkuser.checkuser import exist_user
from connector.models import Search, TaskQueue, SearchResult
from messenger.forms import CreateCampaignForm, CreateCampaignMesgForm, \
    UpdateCampWelcomeForm, InlineCampaignStepFormSet, UpdateCampConnectForm
from messenger.models import Inbox, ContactStatus, Campaign
from django.core.exceptions import ObjectDoesNotExist

User = get_user_model()
decorators = (never_cache, login_required,)


@method_decorator(decorators, name='dispatch')
class AccountList(ListView):
    model = LinkedInUser



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
            
        # add this current account into context for
        ctx['account'] = get_object_or_404(LinkedInUser, pk=ctx['pk'],
                                           user=self.request.user)
        #print('account:', ctx['account'])
        
        if ctx['account'] is None or ctx['account'].status != True:
            print('account:', ctx['account'].status)
            #raise ObjectDoesNotExist 
        
        ctx['inbox_status'] = ContactStatus.inbox_statuses
        
        return ctx

contact_statuses = [ContactStatus.CONNECTED_N, ContactStatus.OLD_CONNECT_N]

@method_decorator(decorators, name='dispatch')
class AccountDetail(AccountMixins, DetailView):
    template_name = 'app/accounts_detail.html'
    model = LinkedInUser
    status = contact_statuses
    
    def get_context_data(self, **kwargs):
        ctx = super(AccountDetail, self).get_context_data(**kwargs)
        # count connection number by
        linkedIn_user = ctx['object']
        
        ctx['connection_count'] = Inbox.objects.filter(owner=linkedIn_user,
                                                       status__in=self.status).count()
        camp_qs = Campaign.objects.filter(owner=linkedIn_user)
        ctx['messengers'] = camp_qs.filter(is_bulk=True)
        ctx['connectors'] = camp_qs.filter(is_bulk=False)
        ctx['account_home'] = True

        return ctx


@method_decorator(decorators, name='dispatch')
class AccountSettings(UpdateView):
    model = LinkedInUser
    fields = ['start_from', 'start_to', 'is_weekendwork', 'tz', 'status']
    template_name = 'app/accounts_settings.html'

    def get_success_url(self):
        return reverse('account-settings', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super(AccountSettings, self).get_context_data(**kwargs)
        context['connections'] = len(Inbox.objects.filter(owner=self.object, is_connected=True))
        return context


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
                BotTask(owner=linkedin_user, task_type=BotTaskType.LOGIN,
                    name='add linkedin account').save()

        return redirect('accounts')

@method_decorator(csrf_exempt_decorators, name='dispatch')
class AccountInfo(View):
    
    def add_sync_data_task(self, linkedin_user):
        contact_task = BotTask.objects.get(owner=linkedin_user, 
                                           task_type=BotTaskType.CONTACT)
        message_task = BotTask.objects.get(owner=linkedin_user, 
                                           task_type=BotTaskType.MESSAGING)
        contact_task.name = 'Get contacts of  linkedin account'
        contact_task.save()
        
        message_task.name='Get contacts of  linkedin account'
        message_task.save()
        
    def update_data_sync(self,linkedin_user):
        membership = Membership.objects.get(user=linkedin_user.user)
        linkedin_user.latest_login = datetime.datetime.now()
        linkedin_user.status = True
        linkedin_user.save()
        linkedin_user.membership.add(membership)
            
    def check_data_sync(self, linkedin_user):
        contact_task = BotTask.objects.get(owner=linkedin_user, 
                                           task_type=BotTaskType.CONTACT)
        message_task = BotTask.objects.get(owner=linkedin_user, 
                                           task_type=BotTaskType.MESSAGING)
        
        if contact_task.status == BotTaskStatus.DONE and (
            message_task.status == BotTaskStatus.DONE):
            # sync done
            self.update_data_sync(linkedin_user)
            return HttpResponse('<script> window.location.href = "/accounts/"; </script>')
        
        return HttpResponse(BotTaskType.DATA_SYNC)
        
    def post(self, request):
        print(request.POST)
        if 'email' in request.POST.keys() and 'password' in request.POST.keys():
            user_email = request.POST['email'].strip()
            user_password = request.POST['password'].strip()
            req_task_type = request.POST.get('task_type', '')
            
            linkedin_user = LinkedInUser.objects.get(email=user_email,password=user_password)
            
            if req_task_type == BotTaskType.DATA_SYNC:
                return self.check_data_sync(linkedin_user)
            
            bot_task = BotTask.objects.get(owner=linkedin_user, task_type=BotTaskType.LOGIN)

            if bot_task.status == BotTaskStatus.PIN_REQUIRED:
                return HttpResponse(render_to_string('app/pinverify.html',{'object':linkedin_user}))
            elif bot_task.status == BotTaskStatus.PIN_INVALID:
                return HttpResponse(render_to_string('app/pinverify.html',{'object':linkedin_user, 'error':True}))
            elif bot_task.status == BotTaskStatus.DONE :
                
                #return HttpResponse('<script> window.location.href = "/accounts/"; </script>')
                # not done yet
                self.add_sync_data_task(linkedin_user) 
                return HttpResponse(BotTaskType.DATA_SYNC)
            elif bot_task.status == BotTaskStatus.PIN_CHECKING :
                return HttpResponse('pin checking')
            elif bot_task.status == BotTaskStatus.ERROR :
                return HttpResponse(render_to_string('app/account_add_error.html'))
            else:
                return HttpResponse('Processing')
        if 'id' in request.POST.keys() and 'pin' in request.POST.keys():
            id_ = int(request.POST['id'].strip())

            pin = request.POST['pin'].strip()
            linkedin_user = LinkedInUser.objects.get(id=id_)
            bot_task = BotTask.objects.get(owner=linkedin_user, task_type=BotTaskType.LOGIN)
            bot_task.extra_info = json.dumps({'pin':pin})
            bot_task.status = BotTaskStatus.PIN_CHECKING
            bot_task.save()
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


class AjaxDatatableResponse(object):
    pass


def Datedefault(o):
        if type(o) is datetime.date or type(o) is datetime.datetime:
            return o.strftime("%d/%m/%Y @ %H:%M")
        
class DataTable(object):
    is_connected = False
    model = Inbox
    result_list = ('id', 'name', 'company', 'industry', 'title',
                    'location', 'latest_activity', 'campaigns__title', 'status')
    
    
    
    
    def render_to_response(self, context, **response_kwargs):
        if self.request.is_ajax():
            #data = serializers.serialize('json', context['object_list'])
            data = [list(x) for x in context['object_list']]
            
                      
            json_data = json.dumps(dict(data=data), default=Datedefault)
            return HttpResponse(json_data, content_type='application/json')
            
        return super(DataTable, self).render_to_response(context, **response_kwargs)
    # override this for custom list
    def get_queryset(self):
        qs = super(DataTable, self).get_queryset()
        qs = qs.filter(owner_id=self.kwargs.get('pk'))
        
        # if 'my network' should limit 'connected' or 'old connected'
        if self.is_connected:
            qs = qs.filter(is_connected=self.is_connected)
            
        
        if self.request.is_ajax():
            qs = qs.values_list(*self.result_list)
        return qs
    
    def get_context_data(self, **kwargs):
        ctx = super(DataTable, self).get_context_data(**kwargs)
        if self.request.is_ajax():
            return ctx
            
        #ctx['inbox_status'] = ContactStatus.inbox_statuses
        
        ctx['object_list'] = []
        
        return ctx

@method_decorator(decorators, name='dispatch')
class AccountNetwork(AccountMixins, DataTable, ListView):
    template_name = 'app/accounts_network.html'
    status = contact_statuses
    is_connected = False
    
    def get_context_data(self, **kwargs):
        ctx = super(AccountNetwork, self).get_context_data(**kwargs)
        ctx['messenger_campaigns'] = ctx['account'].get_messenger_campaigns()
        ctx['messenger_campaigns_count'] = len(ctx['messenger_campaigns'])
        
        return ctx
    
        

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
        campaigns = Campaign.objects.filter(owner__pk=pk)
        return render(request, self.template_name,{'searches': searches, 'pk':pk, 'campaigns':campaigns})

    def post(self, request, pk):

        search_form = SearchForm(request.POST)
        if search_form.is_valid():
            search = search_form.save(commit=False)
            linkedin_user = LinkedInUser.objects.get(pk=pk)
            search.owner = linkedin_user
            search.save()
            TaskQueue(content_object=search).save()
        return HttpResponseRedirect(reverse('account-search', args=[pk]))

@method_decorator(decorators, name='dispatch')
class AccountSearchDelete(View):
    template_name = 'app/accounts_search.html'
    def post(self, request, pk, search_id):

        Search.objects.filter(owner__pk=pk, pk=search_id).delete()
        return HttpResponseRedirect(reverse('account-search', args=[pk]))


@method_decorator(decorators, name='dispatch')
class AccountInbox(AccountMixins, DataTable, ListView):
    template_name = 'app/accounts_inbox.html'
    

@method_decorator(decorators, name='dispatch')
class AccountTask(AccountMixins, ListView):
    template_name = 'app/accounts_task.html'
    model = TaskQueue
    

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
        #print('data:', self.kwargs, data)
        
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
    ##result_list = ('id', 'name', 'company', 'industry', 'title',
    ##               'location', 'latest_activity', 'campaigns__title', 'status')
    def render_to_response(self, context, **response_kwargs):
        if self.request.is_ajax():
            #data = serializers.serialize('json', context['object_list'])
            data = [[x.id, x.name, x.company, x.industry,
                         x.title, x.location, x.latest_activity,
                         "", x.status] for x in context['object'].contacts.all()]
            print('data:', data)
                      
            json_data = json.dumps(dict(data=data), default=Datedefault)
            return HttpResponse(json_data, content_type='application/json')
            
        return super(AccountMessengerDetail, self).render_to_response(context, **response_kwargs)

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
        if 'search_head' not in request.POST.keys() or (not request.POST['search_head'].isdigit()):
            return render(request,'app/search_render/search_select.html')
        print(request.POST['search_head'])
        search_id = int(request.POST['search_head'])
        search = get_object_or_404(Search,pk=search_id, owner__user=request.user)
        if not search.result_status():
            return render(request, 'app/search_render/search_waiting.html')

        if not search.result_count():
            return render(request, 'app/search_render/no_search_result.html')

        item = []
        if 'selected_items[]' in request.POST.keys():
            item = list( map(int, request.POST.getlist('selected_items[]')))
        elif 'selected_items' in request.POST.keys():
            item += [int(request.POST.get('selected_items'))]
        elif 'add_all_selected_item_button' in request.POST.keys():
            search_results = SearchResult.objects.filter(search=search, status=None)
            search_results.update(status=ContactStatus.IN_QUEUE_N)

        if item:
            if 'campaign' in request.POST.keys():
                search_results = SearchResult.objects.filter(search=search, pk__in=item)
                search_results.update(status=ContactStatus.IN_QUEUE_N)



        search_results = SearchResult.objects.filter(search=search)
        return render(request, 'app/search_render/search_render.html', {'search':search, 'search_results':search_results})




