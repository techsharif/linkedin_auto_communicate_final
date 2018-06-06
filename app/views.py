from smtplib import SMTPException

from django.contrib.auth import get_user_model, authenticate, login, logout
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.template.loader import render_to_string

from django.urls.base import reverse_lazy, reverse
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views import View
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView
from .models import AdminEmail
from app.forms import UserRegisterForm
from app.models import MembershipType, Membership, LinkedInUser
from app.tokens import account_activation_token
from django.utils import timezone
from datetime import timedelta
import datetime
from django.conf import settings

User = get_user_model()


# New views

def RegisterView(request):
    msg = ''
    email = ''
    password = ''
    if request.POST:
        email = request.POST.get('email')
        password = request.POST.get('password')
        print(email)
        user = User.objects.filter(email=email).first()
        if user is not None:
            msg="email_exists"
        else:
            user = User()
            user.username = email
            user.is_active = False
            user.email = email
            user.password = password
            user.set_password(password)
            user.save()

            site_name = get_current_site(request)
            # todo: change hard code subject
            subject = 'Activate account'

            # generate message
            # print(urlsafe_base64_encode(force_bytes(user.pk)))
            message = render_to_string('app/account_activation_email.html', {
                'user': user,
                'domain': site_name.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode("utf-8"),
                'token': account_activation_token.make_token(user),
            })
            msg = "register_success"
            # send activation link to the user
            user.email_user(subject, message)

    return render(request, 'v2/registration/register.html', {
    'msg': msg, 'email': email, 'password': password})


def LoginView(request):
    msg=''
    if request.POST:
        email = request.POST.get('email')
        password = request.POST.get('password')
        print(email)
        print(password)
        USER = authenticate(username=email, password=password)
        print(USER)
        if USER is not None:
            USER.is_active = True
            USER.save()
            login(request, USER)
            # add membership only
            # profile = user.profile
            # if profile.day_to_live <= 0:
            membership_type, created = MembershipType.objects.get_or_create(name='Free')
            membership_add_subscription(USER, membership_type, True)
            redirect_url = '/accounts'
            return HttpResponseRedirect(redirect_url)
        else:
            msg = "invalid_user"

    return render(request, 'v2/registration/login.html',{'msg' : msg})


def home(request):
    return render(request, 'home/base.html')


def new_landing(request):
    return render(request, 'new/landing/base.html')


def new_auth(request):
    return render(request, 'new/auth/base.html')


class HomeView(TemplateView):
    template_name = 'v2/app/home.html'
    models = MembershipType

    def get(self, request):
        if request.user.is_authenticated:
            redirect_url = '/accounts'
            return HttpResponseRedirect(redirect_url)
        else:
            return render(request, self.template_name)

    def get_context_data(self, **kwargs):
        ctx = super(HomeView, self).get_context_data(**kwargs)
        for x in MembershipType.objects.all():
            ctx[x.name] = x

        return ctx


class SubsriptionView(TemplateView):
    template_name = 'app/subscription.html'
    models = MembershipType

    def get_context_data(self, **kwargs):
        ctx = super(SubsriptionView, self).get_context_data(**kwargs)
        for x in MembershipType.objects.all():
            ctx[x.name] = x

        return ctx


class ProfileView(TemplateView):
    template_name = 'app/profile.html'


def membership_add_subscription(user, membership_type, active=False):
    valid_from = timezone.now()
    valid_to = valid_from + timedelta(days=membership_type.day_to_live)

    membership = Membership(user=user, membership_type=membership_type,
                            valid_to=valid_to, valid_from=valid_from,
                            updated_at=valid_from, active=active)
    membership.save()


class ActivateAccount(View):
    template_name = "registration/invalid_activation.html"

    def get(self, request, uidb64, token):
        try:
            uid = force_text(urlsafe_base64_decode(uidb64.encode("utf-8")))
            user = User.objects.get(pk=uid)
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        if user is not None and account_activation_token.check_token(user, token):
            user.is_active = True
            user.save()
            # send welcome email to user
            # site_name = get_current_site(self.request)
            # todo: change hard code subject
            subject = 'Getting started with {0}'.format(settings.SITE_TITLE)
            message = render_to_string('app/account_activated_email.html', {
                'current_date': datetime.datetime.now().strftime('%Y-%m-%d'),
                'site_title': settings.SITE_TITLE,
                'user': user,
            })
            # send activation link to the user
            bccs = AdminEmail.objects.all()
            send_bcc = []
            for bcc in bccs:
                send_bcc.append(bcc.email)
            # bcc is not working
            print(send_bcc)
            # user.email_user(subject, message, None, send_bcc)
            msg = EmailMessage(subject, message, None, [user.email], send_bcc)
            msg.send()
            # user.email_user(subject, message)

            login(request, user)
            # add membership only
            # profile = user.profile
            # if profile.day_to_live <= 0:
            membership_type, created = MembershipType.objects.get_or_create(name='Free')
            membership_add_subscription(user, membership_type, True)

            #    membership.membership_type.add(membership_type)
            #    profile.day_to_live = membership_type.day_to_live

            return HttpResponseRedirect(reverse('accounts'))
        else:
            return render(request, self.template_name)
