
from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponse
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView, View
from django.views.generic.list import ListView
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from app.models import LinkedInUser

decorators = (login_required,)


@method_decorator(decorators, name='dispatch')
class AccountList(ListView):
    model = LinkedInUser


@method_decorator(decorators, name='dispatch')
class AccountDetail(TemplateView):
    template_name = 'app/accounts_detail.html'


@method_decorator(decorators, name='dispatch')
class AccountSettings(TemplateView):
    template_name = 'app/accounts_settings.html'


@method_decorator(decorators, name='dispatch')
class AccountAdd(View):
    def get(self, request):
        # if 'email' in request.POST.keys() and 'password' in request.POST.keys():
        if True:
            # user_email = request.POST['email'].strip()
            # user_password = request.POST['password'].strip()

            user_email = 'mdrichardson@communitygurumarketing.com'
            user_password = 'Snow1007!'

            driver = webdriver.Chrome()
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

            return HttpResponse('ok')


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


