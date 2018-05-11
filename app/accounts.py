import datetime

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http.response import HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView, View
from django.views.generic.list import ListView
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC, wait
from django.contrib.auth import get_user_model

from app.forms import PinForm
from app.models import LinkedInUser, Membership, BotTask
from checkuser.checkuser import exist_user
from django.views.generic.detail import DetailView
from messenger.models import Inbox, ContactStatus

decorators = (login_required,)
User = get_user_model()


@method_decorator(decorators, name='dispatch')
class AccountList(ListView):
    model = LinkedInUser


@method_decorator(decorators, name='dispatch')
class AccountDetail(DetailView):
    template_name = 'app/accounts_detail.html'
    model = LinkedInUser

    def get_context_data(self, **kwargs):
        ctx = super(AccountDetail, self).get_context_data(**kwargs)
        # count connection number by
        linkedIn_user = ctx['object']
        statuses = [ContactStatus.CONNECTED, ContactStatus.OLD_CONNECT]
        ctx['connection_count'] = Inbox.objects.filter(owner=linkedIn_user,
                                                       status__in=statuses).count()
        return ctx


@method_decorator(decorators, name='dispatch')
class AccountSettings(View):
    template_name = 'app/accounts_settings.html'

    def get(self, request, pk):
        # get linkedin user data using pk
        linkedin_user = get_object_or_404(LinkedInUser, pk=pk)
        return render(request, self.template_name, {'linkedin_user': linkedin_user})

    def post(self, request, pk):
        # get linkedin user data using pk
        linkedin_user = get_object_or_404(LinkedInUser, pk=pk)

        # update settings
        linkedin_user.start_from = request.POST.get('schedule[from]', linkedin_user.start_from)
        linkedin_user.start_to = request.POST.get('schedule[to]', linkedin_user.start_to)
        linkedin_user.is_weekendwork = bool(request.POST.get('schedule[weekend]', linkedin_user.is_weekendwork))
        linkedin_user.tz = request.POST.get('schedule[tz]', linkedin_user.tz)

        # save update
        linkedin_user.save()

        return render(request, self.template_name, {'linkedin_user': linkedin_user})


@method_decorator(decorators, name='dispatch')
class AccountAdd(View):
    def post(self, request):
        if 'email' in request.POST.keys() and 'password' in request.POST.keys():
            user_email = request.POST['email'].strip()
            user_password = request.POST['password'].strip()
            # collect membership data of this user
            membership = Membership.objects.get(user=request.user)

            # create of get linkedin user
            linkedin_user, created = LinkedInUser.objects.get_or_create(user=request.user, email=user_email,
                                                                        password=user_password)
            linkedin_user.latest_login = datetime.datetime.now()
            linkedin_user.save()
            linkedin_user.membership.add(membership)

            BotTask(owner=linkedin_user, task_type='add account', name='add linkedin account').save()

        return redirect('accounts')


@method_decorator(decorators, name='dispatch')
class AccountNetwork(TemplateView):
    template_name = 'app/accounts_network.html'


@method_decorator(decorators, name='dispatch')
class AccounMessenger(TemplateView):
    template_name = 'app/accounts_messenger.html'


@method_decorator(decorators, name='dispatch')
class AccountCampaign(TemplateView):
    template_name = 'app/accounts_campaign.html'


@method_decorator(decorators, name='dispatch')
class AccountSearch(TemplateView):
    template_name = 'app/accounts_search.html'


@method_decorator(decorators, name='dispatch')
class AccountInbox(TemplateView):
    template_name = 'app/accounts_inbox.html'


@method_decorator(decorators, name='dispatch')
class AccountTask(TemplateView):
    template_name = 'app/accounts_task.html'


@method_decorator(decorators, name='dispatch')
class AccounMessengerCreate(TemplateView):
    template_name = 'app/accounts_messenger_add.html'


@method_decorator(decorators, name='dispatch')
class AccountCampaignCreate(TemplateView):
    template_name = 'app/accounts_campaign_add.html'


def can_add_account(user):
    # check if the current user can add more linked account
    pass


def remove_account(request, pk):
    LinkedInUser.objects.get(id=pk).delete()
    return redirect('accounts')
