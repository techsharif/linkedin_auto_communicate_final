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

from app.forms import UserRegisterForm
from app.models import MembershipType, Membership, LinkedInUser
from app.tokens import account_activation_token
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


# New views


def RegisterView_NEW(request):
    msg=''
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
            msg="register_success"
            # send activation link to the user
            user.email_user(subject, message)

        print( "msg = ")
        print (msg)
    return render(request, 'v2/registration/register.html',{'msg':msg})


def LoginView_NEW(request):
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
            ## add membership only
            # profile = user.profile
            # if profile.day_to_live <= 0:
            membership_type, created = MembershipType.objects.get_or_create(name='Free')
            membership_add_subscription(USER, membership_type, True)
            redirect_url='/accounts'
            return HttpResponseRedirect(redirect_url)
        else:
            msg="invalid_user"

    return render(request, 'v2/registration/login.html',{'msg' : msg})




# def Test_NEW(request):
#     return render(request, 'v2/app/test.html')

class HomeView_NEW(TemplateView):
    template_name = 'v2/app/home.html'

    def get_context_data(self, **kwargs):
        ctx = super(HomeView_NEW, self).get_context_data(**kwargs)
        for x in MembershipType.objects.all():
            ctx[x.name] = x
        # print('ctx:', ctx)
        return ctx




# OLD Views


def home(request):
    return render(request, 'home/base.html')

def new_landing(request):
    return render(request, 'new/landing/base.html')


def new_auth(request):
    return render(request, 'new/auth/base.html')

class HomeView(TemplateView):
    template_name = 'app/home.html'
    print("template_name = " + template_name)
    def get_context_data(self, **kwargs):
        ctx = super(HomeView, self).get_context_data(**kwargs)
        for x in MembershipType.objects.all():
            ctx[x.name] = x
        # print('ctx:', ctx)
        return ctx





class RegisterView(CreateView):
    form_class = UserRegisterForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('register_done')

    def form_invalid(self, form):
        # print('invalid:', form.errors)
        return super(RegisterView, self).form_invalid(form)

    def form_valid(self, form):
        # return CreateView.form_valid(self, form)

        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.email
            user.is_active = False
            user.save()
            # create profile
            # may be not use this model for now
            # Profile(user=user).save()

            # send validate email

            # collect site name
            site_name = get_current_site(self.request)
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

            # send activation link to the user
            user.email_user(subject, message)

            return super(RegisterView, self).form_valid(form)
        else:

            return super(RegisterView, self).form_invalid(form)


class SubsriptionView(TemplateView):
    template_name = 'app/subscription.html'


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
            login(request, user)
            ## add membership only
            # profile = user.profile
            # if profile.day_to_live <= 0:
            membership_type, created = MembershipType.objects.get_or_create(name='Free')
            membership_add_subscription(user, membership_type, True)

            #    membership.membership_type.add(membership_type)
            #    profile.day_to_live = membership_type.day_to_live

            return HttpResponseRedirect(reverse('accounts'))
        else:
            return render(request, self.template_name)
