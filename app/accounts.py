import datetime
import json

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls.base import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import TemplateView, View
from django.views.generic.detail import DetailView, BaseDetailView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC, wait
from selenium.webdriver.support.ui import WebDriverWait

from app.forms import PinForm
from app.models import LinkedInUser, Membership, BotTask
from checkuser.checkuser import exist_user
from messenger.forms import CreateCampaignForm, CreateCampaignMesgForm
from messenger.models import Inbox, ContactStatus, Campaign


User = get_user_model()
decorators = (never_cache, login_required,)

@method_decorator(decorators, name='dispatch')
class AccountList(ListView):
    model = LinkedInUser


class AccountMixins(object):
    def get_context_data(self, **kwargs):
        ctx = super(AccountMixins, self).get_context_data(**kwargs)
        if 'acc_pk' in self.kwargs:
            ctx['acc_pk'] = self.kwargs.get('acc_pk')
        else:
            ctx['acc_pk'] = self.kwargs.get('pk')
        
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
class AccountSettings(View):
    template_name = 'app/accounts_settings.html'

    def get(self, request, pk):

        # get linkedin user data using pk
        linkedin_user = get_object_or_404(LinkedInUser,pk=pk)
        return render(request, self.template_name, {'linkedin_user':linkedin_user})

    def post(self, request, pk):
        # get linkedin user data using pk
        linkedin_user = get_object_or_404(LinkedInUser, pk=pk)

        # update settings
        linkedin_user.start_from = request.POST.get('schedule[from]', linkedin_user.start_from)
        linkedin_user.start_to = request.POST.get('schedule[to]', linkedin_user.start_to)
        linkedin_user.is_weekendwork = bool (request.POST.get('schedule[weekend]', linkedin_user.is_weekendwork))
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

            driver = webdriver.Chrome("/usr/lib/chromium-browser/chromedriver")
            driver.get("https://www.linkedin.com")
            wait = WebDriverWait(driver, 2)

            print("------working-----")

            email = wait.until(EC.visibility_of_element_located(
                (By.CSS_SELECTOR, "input#login-email")))
            print("------pass email---------")

            password = wait.until(EC.visibility_of_element_located(
                (By.CSS_SELECTOR, "input#login-password")))
            print("------pass password---------")

            signin_button = wait.until(EC.visibility_of_element_located(
                (By.CSS_SELECTOR, "input#login-submit")))
            print("------pass button---------")

            email.clear()
            password.clear()

            email.send_keys(user_email)
            password.send_keys(user_password)

            signin_button.click()
            print("----------click sign in----------------")

            # check if user is exist
            if exist_user():
                print("That user is an existing user.")
                print("--------pin code step----------")

                # pin code verification
                # todo: pin verification
                try:
                    pincode_input = wait.until(EC.visibility_of_element_located(
                        (By.CSS_SELECTOR, "input#verification-code")))
                    # return redirect('pinverify')
                    return redirect('accounts')
                except Exception as e:
                    print("---sucessfull login without pin code verification!---")

                # collect membership data of this user
                membership = Membership.objects.get(user=request.user)

                # create of get linkedin user
                linkedin_user, created = LinkedInUser.objects.get_or_create(user=request.user, email=user_email, password=user_password)
                linkedin_user.latest_login = datetime.datetime.now()
                linkedin_user.save()
                linkedin_user.membership.add(membership)


            else:
                print("---That user is not exist in Linkedin.---")

        return redirect('accounts')

class InboxMixins(object):
    status_list = None
    
    def get_queryset(self):
        pass
    

@method_decorator(decorators, name='dispatch')
class AccountNetwork(AccountMixins, InboxMixins, ListView):
    template_name = 'app/accounts_network.html'
    

@method_decorator(decorators, name='dispatch')
class AccounMessenger(AccountMixins, ListView):
    template_name = 'app/accounts_messenger.html'
    is_bulk = True
    model = Campaign
    
    def get_queryset(self):
        qs = super(AccounMessenger, self).get_queryset()
        qs = qs.filter(is_bulk=self.is_bulk, owner_id=self.kwargs.get('acc_pk'))
        return qs

@method_decorator(decorators, name='dispatch')
class AccountCampaign(AccounMessenger):
    template_name = 'app/accounts_campaign.html'
    is_bulk = False
    


@method_decorator(decorators, name='dispatch')
class AccountSearch(AccountMixins, TemplateView):
    template_name = 'app/accounts_search.html'


@method_decorator(decorators, name='dispatch')
class AccountInbox(AccountMixins, TemplateView):
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
        acc_id = self.kwargs.get('acc_pk')
        if self.request.method == "POST":
            form = self.form_class(self.request.POST, owner_id=acc_id,
                                   is_bulk=self.is_bulk)
        else:
            form = self.form_class(owner_id=acc_id, is_bulk=self.is_bulk)
        return form
    
    def get_success_url(self):
        
        return reverse_lazy('account-messenger', kwargs=self.kwargs)
    
    def form_invalid(self, form):
        print('form_invalid:', form.is_valid(), form )
        return super(AccountMessengerCreate, self).form_invalid(form)
    
    def form_valid(self, form):
        
        camp = form.instance
        camp.owner_id = self.kwargs.get('acc_pk')
        camp.is_bulk = self.is_bulk
        camp = form.save()
        # if copy step message
        if camp.copy_campaign:
            camp.copy_step_message()
            
        return super(AccountMessengerCreate, self).form_valid(form)
        
        
    
@method_decorator(decorators, name='dispatch')
class AccountCampaignCreate(AccountMessengerCreate):
    template_name = 'app/accounts_campaign_add.html'
    form_class = CreateCampaignForm
    
    def __init__(self, *args, **kwargs):
        super(AccountCampaignCreate, self).__init__()
        self.is_bulk = False
        
    def get_success_url(self):
        return reverse_lazy('account-campaign', kwargs=self.kwargs)


@method_decorator(decorators, name='dispatch')
class AccountMessengerDetail(AccountMixins, UpdateView):
    template_name = 'app/accounts_messenger_update.html'
    model = Campaign
    
@method_decorator(decorators, name='dispatch')
class AccountCampaignDetail(TemplateView):
    template_name = 'app/accounts_campaign_update.html'
    model = Campaign

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
    
csrf_exempt_decorators = decorators + (csrf_exempt, ) 
@method_decorator(csrf_exempt_decorators, name='dispatch')
class AccountBotTask(JSONDetailView):
    template_name = 'app/bottask_detail.html'
    model = BotTask
    
def can_add_account(user):
    # check if the current user can add more linked account
    pass

def remove_account(request, pk):
    linkedin_user = LinkedInUser.objects.get(id=pk)
    BotTask(owner=linkedin_user, task_type='delete', name='remove linkedin account').save()
    return redirect('accounts')



