import datetime
import json
import re
import calendar
from dateutil.relativedelta import relativedelta

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
from app.models import LinkedInUser, Membership, BotTask, BotTaskType, BotTaskStatus, FreeBotIP

from checkuser.checkuser import exist_user
from connector.models import Search, TaskQueue, SearchResult
from messenger.forms import CreateCampaignForm, CreateCampaignMesgForm, \
    UpdateCampWelcomeForm, InlineCampaignStepFormSet, UpdateCampConnectForm, STEP_TIMES
from messenger.models import Inbox, ContactStatus, Campaign, ChatMessage, CampaignStep
from django.core.exceptions import ObjectDoesNotExist

from messenger.utils import calculate_communication_stats, calculate_connections, calculate_dashboard_data, \
    calculate_connection_stat_graph, calculate_map_data

User = get_user_model()
decorators = (never_cache, login_required,)
csrf_exempt_decorators = decorators + (csrf_exempt,)


def calculate_report_data(owner,start_date,end_date):
    campaigns = Campaign.objects.filter(owner=owner, is_bulk=False,created_at__range=(start_date,end_date))
    campaign_members = 0
    connected_members = 0
    inv_accept = 0
    for campaign in campaigns:
        campaign_members_list = campaign.contacts.all()
        campaign_members += len(campaign_members_list)
        connected_members += len(campaign_members_list.filter(is_connected=True).exclude(connected_date=None))
        inv_accept += len(campaign_members_list.filter(is_connected=True,connected_date__range=(start_date,end_date)))
    all_chat_messages = ChatMessage.objects.filter(owner=owner, campaign__is_bulk=False)

    invitations_sent = len(all_chat_messages.filter(type=ContactStatus.CONNECT_REQ_N))
    replied = len(all_chat_messages.exclude(replied_date=None))

    return {
        'accept_inv':inv_accept,
        'campaign_members': campaign_members,
        'connected_members': connected_members,
        'invitations_sent': invitations_sent,
        'invitation_rate': int(invitations_sent / campaign_members) if campaign_members else 0,
        'pending_rate': 100 - int(invitations_sent / campaign_members) if campaign_members else 0,
        'replied': replied,
        'campaign_members_p': int(
            max(campaign_members, invitations_sent, replied) / campaign_members * 100) if campaign_members else 0,
        'invitations_sent_p': int(
            max(campaign_members, invitations_sent, replied) / invitations_sent * 100) if invitations_sent else 0,
        'replied_p': int(max(campaign_members, invitations_sent, replied) / replied * 100) if replied else 0,
       
    }



def cleanhtml(raw_html):
  cleanr = re.compile('<.*?>')
  cleantext = re.sub(cleanr, '', raw_html)
  return cleantext

@method_decorator(decorators, name='dispatch')
class AccountList(ListView):
    model = LinkedInUser
    template_name = 'account/accounts.html'

    def get_queryset(self):
        qs = super(AccountList, self).get_queryset()
        qs = qs.filter(user=self.request.user)
        return qs

@method_decorator(decorators, name='dispatch')
class RemoveAccount(View):
    def get(self, request, pk):
        linekedin_user = LinkedInUser.objects.get(id=pk)
        if linekedin_user.bot_ip:
            FreeBotIP(bot_ip=linekedin_user.bot_ip).save()
        linekedin_user.delete()
        return redirect('/accounts')


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
        ctx['apk'] = self.kwargs.get('pk')

        # add this current account into context for
        ctx['account'] = get_object_or_404(LinkedInUser, pk=ctx['pk'],
                                           user=self.request.user)
        # print('account:', ctx['account'])

        if ctx['account'] is None or ctx['account'].status != True:
            print('account:', ctx['account'].status)
            # raise ObjectDoesNotExist

        ctx['inbox_page_statuses'] = ContactStatus.inbox_page_statuses
        ctx['mynetwork_page_statuses'] = ContactStatus.mynetwork_page_statuses

        return ctx


contact_statuses = [ContactStatus.CONNECTED_N, ContactStatus.OLD_CONNECT_N]


@method_decorator(decorators, name='dispatch')
class AccountDetail(AccountMixins, DetailView):
    template_name = 'v2/account/account_details.html'
    model = LinkedInUser
    status = contact_statuses

    def get_context_data(self, **kwargs):
        ctx = super(AccountDetail, self).get_context_data(**kwargs)
        # count connection number by
        linkedIn_user = ctx['object']
        ctx['linkedin_user'] = self.object
        ctx['pk'] = self.object.pk
        ctx['connection'] = calculate_connections(self.object.pk, self.status)
        camp_qs = Campaign.objects.filter(owner=linkedIn_user)
        ctx['messengers'] = camp_qs.filter(is_bulk=True)
        ctx['connectors'] = camp_qs.filter(is_bulk=False)
        ctx['account_home'] = True
        ctx['upcoming_tasks'] = TaskQueue.objects.filter(owner=self.object).exclude(status=BotTaskStatus.DONE)
        ctx['calculate_communication_stats'] = calculate_communication_stats(self.object.pk)
        ctx['total_campaign_contact_list'] = Inbox.objects.filter(owner=self.object)
        ctx['dashboard_data'] = calculate_dashboard_data(self.object)
        ctx['connection_stat'] = calculate_connection_stat_graph(self.object)
        ctx['map'] = calculate_map_data(self.object)

        return ctx


@method_decorator(decorators, name='dispatch')
class AccountSettings(UpdateView):
    model = LinkedInUser
    fields = ['start_from', 'start_to', 'is_weekendwork', 'tz', 'status','message_limit_default']
    template_name = 'account/account_settings.html'

    def get_success_url(self):
        return reverse('account-settings', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super(AccountSettings, self).get_context_data(**kwargs)
        context['connections'] = len(Inbox.objects.filter(owner=self.object, is_connected=True))
        context['linkedin_user'] = self.object
        context['pk'] = self.object.pk
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

            bot_ip = None
            try:
                is_user = LinkedInUser.objects.get(email=user_email)
                if is_user.status == False:
                    bot_ip = is_user.bot_ip
                    is_user.delete()
                else:
                    return HttpResponse('400', status=400)
            except:
                pass

            linkedin_user = LinkedInUser(user=request.user, email=user_email, password=user_password)
            linkedin_user.save()
            if not bot_ip:
                try:
                    bot_ip = FreeBotIP.objects.filter()[:1].get()
                    linkedin_user.bot_ip = bot_ip.bot_ip
                    linkedin_user.save()
                    bot_ip.delete()
                except:
                    pass
            else:
                linkedin_user.bot_ip = bot_ip
                linkedin_user.save()

            BotTask(owner=linkedin_user, task_type=BotTaskType.LOGIN,
                    name='add linkedin account').save()

        return redirect('accounts')


@method_decorator(csrf_exempt_decorators, name='dispatch')
class AccountInfo(View):

    def check_data_sync(self, linkedin_user):

        """ may be this can be done when contacts is done? """
        # messaging will be called after contacts
        # check message and contact task is already in here or not
        # message_task, message_task_created = BotTask.objects.get_or_create(owner=linkedin_user, task_type=BotTaskType.MESSAGING)

        contact_task, contact_task_created = BotTask.objects.get_or_create(owner=linkedin_user,
                                                                           task_type=BotTaskType.CONTACT)

        # if not created than add the message task name and contact task name
        if contact_task_created:

            # message_task.name = 'Get messageing of  linkedin account'
            # message_task.save()
            contact_task.name = 'Get contacts of  linkedin account'
            contact_task.save()
        else:
            # check if sync complete
            if contact_task.status == BotTaskStatus.DONE:
                self.update_data_sync(linkedin_user)  # if sync complete add a membership
                return True
        return False

    def update_data_sync(self, linkedin_user):
        linkedin_user.activate()

    def post(self, request):
        print(request.POST)
        if 'email' in request.POST.keys() and 'password' in request.POST.keys():

            # collect email and password
            user_email = request.POST['email'].strip()
            user_password = request.POST['password'].strip()

            # collect linkedin user using this email and password
            linkedin_user = LinkedInUser.objects.get(email=user_email, password=user_password)

            # collect the bottask to add the linkedin account
            bot_task = BotTask.objects.get(owner=linkedin_user, task_type=BotTaskType.LOGIN)

            # check different status and pop up
            if bot_task.status == BotTaskStatus.PIN_REQUIRED:
                return HttpResponse(render_to_string('account/accounts/pinverify.html', {'object': linkedin_user}))
            elif bot_task.status == BotTaskStatus.PIN_INVALID:
                return HttpResponse(
                    render_to_string('account/accounts/pinverify.html', {'object': linkedin_user, 'error': True}))
            elif bot_task.status == BotTaskStatus.DONE:
                # not done yet
                if self.check_data_sync(linkedin_user):
                    return HttpResponse(render_to_string('account/accounts/activate.html'))
                else:
                    return HttpResponse(render_to_string('account/accounts/data_sync.html',  {'object': linkedin_user}))
            elif bot_task.status == BotTaskStatus.PIN_CHECKING:
                return HttpResponse(render_to_string('account/accounts/pin_checking.html'))
            elif bot_task.status == BotTaskStatus.ERROR:
                return HttpResponse(render_to_string('account/accounts/account_add_error.html'))
            else:
                return HttpResponse(render_to_string('account/accounts/email_password_config.html'))

        if 'id' in request.POST.keys() and 'pin' in request.POST.keys():  # for pin verification
            id_ = int(request.POST['id'].strip())
            pin = request.POST['pin'].strip()
            linkedin_user = LinkedInUser.objects.get(id=id_)
            bot_task = BotTask.objects.get(owner=linkedin_user, task_type=BotTaskType.LOGIN)
            bot_task.extra_info = json.dumps({'pin': pin})
            bot_task.status = BotTaskStatus.PIN_CHECKING
            bot_task.save()
            return HttpResponse(render_to_string('account/accounts/pin_checking.html'))


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
                   'location', 'latest_activity', 'campaigns__title',
                   'status', 'campaigns__is_bulk')

    def render_to_response(self, context, **response_kwargs):
        if self.request.is_ajax():
            # data = serializers.serialize('json', context['object_list'])
            # data = [list(x) for x in context['object_list']]
            _data = []
            for x in context['object_list']:
                list_data = list(x)
                if list_data[6] is not None:
                    list_data[6] = list_data[6].strftime('%b/%d/%Y %H:%M %p')
                _data.append(list_data)

            json_data = json.dumps(dict(data=_data), default=Datedefault)
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

        # ctx['inbox_status'] = ContactStatus.inbox_statuses

        ctx['object_list_default'] = ctx['object_list']
        for cc in ctx['object_list_default']:
            print('--------', cc.__dict__, '\n')
            pass
        ctx['object_list'] = []

        return ctx


@method_decorator(decorators, name='dispatch')
class AccountNetwork(AccountMixins, DataTable, ListView):
    template_name = 'account/account_network.html'
    status = contact_statuses
    is_connected = True

    def get_context_data(self, **kwargs):
        ctx = super(AccountNetwork, self).get_context_data(**kwargs)
        ctx['messenger_campaigns'] = ctx['account'].get_messenger_campaigns()
        ctx['messenger_campaigns_count'] = len(ctx['messenger_campaigns'])
        return ctx


@method_decorator(decorators, name='dispatch')
class AccounMessenger(AccountMixins, ListView):
    template_name = 'v2/account/account_messenger.html'
    is_bulk = True
    model = Campaign

    def get_queryset(self):
        qs = super(AccounMessenger, self).get_queryset()
        qs = qs.filter(is_bulk=self.is_bulk, owner_id=self.kwargs.get('pk'))
        return qs

    def get_context_data(self, **kwargs):
        ctx = super(AccounMessenger, self).get_context_data(**kwargs)
        ctx['linkedin_user'] = ctx['account']

        return ctx


@method_decorator(decorators, name='dispatch')
class AccountCampaign(AccounMessenger):
    template_name = 'account/account_connect.html'
    is_bulk = False


@method_decorator(decorators, name='dispatch')
class AccountSearch(View):
    template_name = 'v2/account/account_search.html'

    def get(self, request, pk):
        searches = Search.objects.filter(owner__pk=pk)
        campaigns = Campaign.objects.filter(owner__pk=pk, is_bulk=False)
        linkedin_user = LinkedInUser.objects.get(user=request.user, pk=pk)
        return render(request, self.template_name,
                      {'searches': searches, 'pk': pk, 'campaigns': campaigns, 'linkedin_user': linkedin_user})

    def post(self, request, pk):
        search_form = SearchForm(request.POST)
        if search_form.is_valid():
            search = search_form.save(commit=False)
            linkedin_user = LinkedInUser.objects.get(pk=pk)
            search.owner = linkedin_user
            search.save()
            BotTask(owner=linkedin_user, name=BotTaskType.SEARCH, task_type=BotTaskType.SEARCH,
                    extra_id=search.id).save()
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
class AccountTask(View):
    template_name = 'account/account_task_queue.html'

    def get(self, request, pk):
        linkedin_user = LinkedInUser.objects.get(pk=pk)
        all_task_queue = TaskQueue.objects.filter(owner=linkedin_user)
        finished_tasks = all_task_queue.filter(status=BotTaskStatus.DONE)
        upcoming_tasks = all_task_queue.exclude(status=BotTaskStatus.DONE)

        context = {'finished_tasks': finished_tasks, 'upcoming_tasks': upcoming_tasks, 'pk': pk}
        context['linkedin_user'] = linkedin_user
        context['pk'] = pk
        return render(request, self.template_name, context)


@method_decorator(decorators, name='dispatch')
class AccountMessengerCreate(AccountMixins, CreateView):
    template_name = 'v2/account/accounts_messenger_add.html'
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
        # print('data:', self.kwargs, data)

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
    template_name = 'account/accounts_campaign_add.html'
    is_bulk = False

    form_class = CreateCampaignForm

    def __init__(self, *args, **kwargs):
        super(AccountCampaignCreate, self).__init__()
        self.is_bulk = False

    def get_success_url(self):
        return reverse_lazy('account-campaign', kwargs=self.kwargs)


@method_decorator(csrf_exempt_decorators, name='dispatch')
class AccountMessengerDelete(AccountMixins, DeleteView):
    model = Campaign

    def delete(self, request, *args, **kwargs):
        print('request')
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
class AccountMessengerDetailNEW(AccountMixins, UpdateView):
    template_name = 'v2/account/accounts_messenger_update.html'
    form_class = UpdateCampConnectForm
    model = Campaign

    def render_to_response(self, context, **response_kwargs):
        if self.request.is_ajax():
            data = [[x.id, x.name, x.company, x.industry,
                     x.title, x.location, x.latest_activity,
                     "", x.status, x.campaigns.first().is_bulk] for x in context['object'].contacts.all()]
            print('data:', data)

            json_data = json.dumps(dict(data=data), default=Datedefault)
            return HttpResponse(json_data, content_type='application/json')

        return super(AccountMessengerDetailNEW, self).render_to_response(context, **response_kwargs)

    def get_context_data(self, **kwargs):
        data = super(AccountMessengerDetailNEW, self).get_context_data(**kwargs)
        row = data['object']
        print('row object:', row, type(row))
        if self.request.POST:
            data['campaignsteps'] = InlineCampaignStepFormSet(self.request.POST,
                                                              instance=row)
        else:
            data['campaignsteps'] = InlineCampaignStepFormSet(instance=row)

        contact_count = row.contacts.all().count()
        message_contacts = []
        reply_contacts = []

        messages = ChatMessage.objects.filter(campaign=row)
        for message in messages:
            if message.is_direct:
                message_contacts += [message.contact.pk]
                if message.replied_date:
                    reply_contacts += [message.contact.pk]

        message_contacts = len(set(message_contacts))
        reply_contacts = len(set(reply_contacts))

        # contact_count = 50
        # message_contacts = 35
        # reply_contacts = 17
        message_percent = int(message_contacts / contact_count * 100) if contact_count else 0
        reply_percent = int(reply_contacts / contact_count * 100) if contact_count else 0
        message_above_50 = True if message_percent > 50 else False
        reply_above_50 = True if reply_percent > 50 else False
        data['contacts_stat'] = {
            'contacts': contact_count,
            'message_contacts': message_contacts,
            'message_percent': message_percent,
            'reply_contacts': reply_contacts,
            'reply_percent': reply_percent,
            'message_above_50': message_above_50,
            'reply_above_50': reply_above_50
        }

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

        return super(AccountMessengerDetailNEW, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('messenger-campaign', kwargs=self.kwargs)

    def form_invalid(self, form):
        print('form invalid:', form.errors)
        if self.request.is_ajax():
            context = dict(error=form.errors)
            json_data = json.dumps(context)
            return HttpResponse(json_data, content_type='application/json')

        return super(AccountMessengerDetailNEW, self).form_invalid(form)




@method_decorator(decorators, name='dispatch')
class AccountMessengerDetail(AccountMixins, UpdateView):
    template_name = 'v2/account/accounts_messenger_update.html'
    form_class = UpdateCampConnectForm
    model = Campaign

    def render_to_response(self, context, **response_kwargs):
        if self.request.is_ajax():
            data = [[x.id, x.name, x.company, x.industry,
                     x.title, x.location, x.latest_activity,
                     "", x.status, x.campaigns.first().is_bulk] for x in context['object'].contacts.all()]
            print('data:', data)

            json_data = json.dumps(dict(data=data), default=Datedefault)
            return HttpResponse('{"ok"}', content_type='application/json')

        return super(AccountMessengerDetail, self).render_to_response(context, **response_kwargs)

    def get_context_data(self, **kwargs):
        data = super(AccountMessengerDetail, self).get_context_data(**kwargs)
        row = data['object']
        print('row object:', row, type(row))
        if self.request.POST:
            data['campaignsteps'] = InlineCampaignStepFormSet(self.request.POST,
                                                              instance=row)
        else:
            data['campaignsteps'] = InlineCampaignStepFormSet(instance=row)

        contact_count = row.contacts.all().count()
        message_contacts = []
        reply_contacts = []

        messages = ChatMessage.objects.filter(campaign=row)
        for message in messages:
            if message.is_direct:
                message_contacts += [message.contact.pk]
                if message.replied_date:
                    reply_contacts += [message.contact.pk]

        message_contacts = len(set(message_contacts))
        reply_contacts = len(set(reply_contacts))

        # contact_count = 50
        # message_contacts = 35
        # reply_contacts = 17
        message_percent = int(message_contacts / contact_count * 100) if contact_count else 0
        reply_percent = int(reply_contacts / contact_count * 100) if contact_count else 0
        message_above_50 = True if message_percent > 50 else False
        reply_above_50 = True if reply_percent > 50 else False
        data['contacts_stat'] = {
            'contacts': contact_count,
            'message_contacts': message_contacts,
            'message_percent': message_percent,
            'reply_contacts': reply_contacts,
            'reply_percent': reply_percent,
            'message_above_50': message_above_50,
            'reply_above_50': reply_above_50
        }

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
        if self.request.is_ajax():
            context = dict(error=form.errors)
            json_data = json.dumps(context)
            return HttpResponse(json_data, content_type='application/json')

        return super(AccountMessengerDetail, self).form_invalid(form)

    def post(self, request, pk):

        print(request.POST)

        if 'cpk' in request.POST.keys():
            type = request.POST['type']
            cpk = request.POST['cpk']

            if type=='save':
                fpk = request.POST['fpk']
                message = request.POST['message']
                message = cleanhtml(message)
                if fpk=='init':
                    campaign = Campaign.objects.get(pk=cpk)
                    campaign.connection_message=message
                    campaign.save()
                else:
                    campaign_step = CampaignStep.objects.get(pk=int(fpk))
                    step = request.POST['step']
                    campaign_step.message = message
                    campaign_step.step_time=step
                    campaign_step.save()
                    return HttpResponse('{"ok":1}', content_type='application/json')
            elif type=='add':
                message = request.POST['message']
                message = cleanhtml(message)
                step = request.POST['step']
                campaign = Campaign.objects.get(pk=cpk)
                CampaignStep(message=message,step_time=step, campaign=campaign).save()

                return HttpResponse('{"ok":1}', content_type='application/json')





@method_decorator(decorators, name='dispatch')
class AccountCampaignDetail(AccountMessengerDetailNEW):
    template_name = 'v2/account/accounts_campaign_update.html'
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


@method_decorator(decorators, name='dispatch')
class RemoveAccount(View):
    def get(self, request, pk):
        linekedin_user = LinkedInUser.objects.get(id=pk)
        if linekedin_user.bot_ip:
            FreeBotIP(bot_ip=linekedin_user.bot_ip).save()
        linekedin_user.delete()
        return redirect('accounts')


@method_decorator(csrf_exempt_decorators, name='dispatch')
class SearchResultView(View):
    def _clone_to_contact(self, qs, campaign):
        # is there a better way to do this??
        for row in qs.all():
            row.attach_to_campaign(campaign)

    def post(self, request):
        print(request.POST)
        if 'search_head' not in request.POST.keys() or (not request.POST['search_head'].isdigit()):
            return render(request, 'account/search_render/search_select.html')
        print(request.POST['search_head'])
        search_id = int(request.POST['search_head'])
        search = get_object_or_404(Search, pk=search_id, owner__user=request.user)
        if not search.result_status():
            return render(request, 'account/search_render/search_waiting.html')

        if not search.result_count():
            return render(request, 'account/search_render/no_search_result.html')

        item = []
        print("request.POST.keys()")
        print(request.POST.keys())
        if 'selected_items[]' in request.POST.keys():
            item = list(map(int, request.POST.getlist('selected_items[]')))
        elif 'selected_items' in request.POST.keys():
            item += [int(request.POST.get('selected_items'))]
        elif 'add_all_selected_item_button' in request.POST.keys():
            if 'campaign' in request.POST.keys():
                campaign = Campaign.objects.get(id=int(request.POST['campaign']))
                search_results = SearchResult.objects.filter(search=search, status=ContactStatus.CONNECT_REQ_N)
                search_results.update(status=ContactStatus.IN_QUEUE_N, connect_campaign=campaign)
                print('here', campaign)
                # self._clone_to_contact(search_results, campaign)

        if item:
            if 'campaign' in request.POST.keys():
                campaign = Campaign.objects.get(id=int(request.POST['campaign']))
                search_results = SearchResult.objects.filter(search=search, pk__in=item)
                # attache to a campagn
                search_results.update(status=ContactStatus.IN_QUEUE_N,
                                      connect_campaign=campaign,)
                self._clone_to_contact(search_results, campaign)
                print('here', campaign)

        search_results = SearchResult.objects.filter(search=search)
        return render(request, 'v2/account/search_render/search_render.html',
                      {'search': search, 'search_results': search_results})


@method_decorator(decorators, name='dispatch')
class AccountTask_NEW(View):
    template_name = 'v2/account/account_task_queue.html'

    def get(self, request, pk):
        linkedin_user = LinkedInUser.objects.get(user_id=pk)
        all_task_queue = TaskQueue.objects.filter(owner=linkedin_user)
        finished_tasks = all_task_queue.filter(status=BotTaskStatus.DONE)
        upcoming_tasks = all_task_queue.exclude(status=BotTaskStatus.DONE)

        context = {'finished_tasks': finished_tasks, 'upcoming_tasks': upcoming_tasks, 'pk': pk}
        context['linkedin_user'] = linkedin_user
        context['pk'] = pk
        return render(request, self.template_name, context)

@method_decorator(decorators, name='dispatch')
class AccountFollowups(View):
    def get(self, request, pk):
        campaign = Campaign.objects.get(pk=pk)
        campaign_steps = CampaignStep.objects.filter(campaign=campaign)
        return render(request, 'v2/messenger/fillowup_list.html', {'campaign_steps':campaign_steps, 'campaign':campaign})

@method_decorator(csrf_exempt_decorators, name='dispatch')
class AccountFollowup(View):
    def post(self, request):
        print(request.POST)
        if 'cpk' in request.POST.keys() and 'fpk' in request.POST.keys():
            cpk = request.POST['cpk']
            fpk = request.POST['fpk']
            data = {}
            data['cpk'] = cpk
            data['fpk'] = fpk
            if fpk == 'init':
                campaign = Campaign.objects.get(pk=int(cpk))
                data['name'] = "Initial Email"
                data['message'] = campaign.connection_message

            else:
                campaign_step = CampaignStep.objects.get(pk=int(fpk))
                data['name'] = "Followup Email"
                data['step_time'] = campaign_step.step_time
                data['message'] = campaign_step.message
                data['steps'] = STEP_TIMES
            return render(request, 'v2/messenger/data_stored.html', data)

@method_decorator(csrf_exempt_decorators, name='dispatch')
class AccountNewFollowup(View):
    def post(self, request):
        data = {}
        data['cpk'] = request.POST['cpk']
        data['steps'] = STEP_TIMES
        return render(request, 'v2/messenger/data_new.html', data)

@method_decorator(decorators, name='dispatch')
class AccountMessengerActive(View):
    def get(self, request, pk):
        campaign = Campaign.objects.get(pk=pk)
        campaign.status = int(request.GET['active'])
        campaign.save()
        return HttpResponse('done')

@method_decorator(csrf_exempt_decorators, name='dispatch')
class AccountFollowupDelete(View):
    def post(self, request):
        fpk = request.POST['fpk']
        campaign_step = CampaignStep.objects.get(pk=int(fpk))
        campaign_step.delete()
        return HttpResponse('done')

@method_decorator(csrf_exempt_decorators, name='dispatch')
class AccountReport(View):
    
    def get(self, request, pk):
        print("pk",request)  
        data={}
        data.update({'pk':pk})
        return render(request, 'v2/account/account_report.html',data)

    def post(self,request,pk):
        data={}
        start =  request.POST.get('opt')
        end = request.POST.get('start')
        last = request.POST.get('start')
        data.update({'pk':pk,"last":last})    
        start_in = start
        end_in = end 
        today = datetime.datetime.now()

        if start == "day":
            end = today - datetime.timedelta(days=int(end))
            start_out =  end
            end_out = today
            data.update({'day':1}) 

        if start == "week":
            week_days = (int(end) * 7)
            st_date = today - datetime.timedelta(days=int(week_days))
            start_out =  st_date
            end_out = today
            data.update({'week':1})

        if start == "month":
            
            st_date = today - relativedelta(months=int(end))
            start_out =  st_date
            end_out = today
            data.update({'month':1}) 

        if start == "quarter":
            
            quarter = (int(end) * 4)
            st_date = today - relativedelta(months=int(quarter))
            start_out =  st_date
            end_out = today
            data.update({'quarter':1})                 


        # start_out = datetime.datetime(*[int(v) for v in start_in.replace('T', '-').replace(':', '-').split('-')])
        
        # end_out = datetime.datetime(*[int(v) for v in end_in.replace('T', '-').replace(':', '-').split('-')])
        
        print ("----",start_out.date(),type(start_out.date()))
        year_filter = start_out.year
        # if end_out < start_out:
            
        #     data.update({'pk':pk,'msg':"End Date is greaterthan start date"})
        #     return render(request, 'v2/account/account_report.html',data)

        # searchobj = Search.objects.filter(owner=pk, searchdate__range=(start_out, end_out))
        # conncetion_request_sent = 0
        # if searchobj:

        #     for obj in searchobj:
        #         request_sent = SearchResult.objects.filter(owner=pk, search=obj.id,
        #                                                    status=ContactStatus.CONNECT_REQ_N).count()
        #         conncetion_request_sent = conncetion_request_sent + request_sent

        # inv_accepted = Inbox.objects.filter(owner_id=pk, connected_date__range=(start_out, end_out)).count()
        # number_of_conn = Inbox.objects.filter(owner_id=pk, is_connected=1).count()
        # year_data = []
        # for x in range(1, 13):
        #     month_con = "Month(connected_date)='" + str(x) + "'"
        #     year_con = "year(connected_date)='" + str(year_filter) + "'"
        #     owner_id = "owner_id='" + str(pk) + "'"
        #     month_x = Inbox.objects.extra(where=[month_con, year_con, owner_id]).count()
        #     year_data.append({'y': month_x, "indexLabel": calendar.month_name[x]})

        # data.update({'pk': pk, 'inv_accepted': inv_accepted, "number_of_conn": number_of_conn,
        #              "conncetion_request_sent": conncetion_request_sent, "graph": json.dumps(year_data),
        #              "year_filter": year_filter})
        # return render(request, 'v2/account/account_report.html', data)
        dash = calculate_report_data(pk,start_out,end_out)                    
        inv_accepted = Inbox.objects.filter(owner_id=pk,connected_date__range=(start_out,end_out)).count()
        inv_accepted_before_start_date = Inbox.objects.filter(owner_id=pk,connected_date__lte=(start_out),is_connected=1).count()
        print("---",inv_accepted_before_start_date)
        number_of_conn = Inbox.objects.filter(owner_id=pk,is_connected=1).count()
        year_data = []
        con_growth = 0
        if inv_accepted_before_start_date > 0:
            con_growth = (number_of_conn - inv_accepted_before_start_date) /(100/inv_accepted_before_start_date)
        # for x in range(1,13):
        #     month_con = "Month(connected_date)='" + str(x) +"'"   
        #     year_con = "year(connected_date)='" + str(year_filter) + "'"
        #     owner_id = "owner_id='" + str(pk) + "'"    
        #     month_x = Inbox.objects.extra(where=[month_con, year_con,owner_id]).count()
        #     year_data.append({'y':month_x,"indexLabel":calendar.month_name[x]})

        
        diff  =  end_out.date() - start_out.date()
        print("------------------con_growth------",con_growth)
        
            
        data.update({'pk':pk,'inv_accepted':dash['accept_inv'],"number_of_conn":number_of_conn,"conncetion_request_sent":dash['invitations_sent'],"year_filter":year_filter,"con_growth":con_growth})
        return render(request, 'v2/account/account_report.html',data)


