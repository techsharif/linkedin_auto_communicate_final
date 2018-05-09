from smtplib import SMTPException

from django.contrib.auth import get_user_model, login
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.http import  HttpResponseRedirect
from django.shortcuts import render
from django.template.loader import render_to_string

from django.urls.base import reverse_lazy, reverse
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views import View
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView

from app.forms import UserRegisterForm
from app.models import MembershipType, Profile, Membership
from app.tokens import account_activation_token

User = get_user_model()


class HomeView(TemplateView):
    template_name = 'app/home.html'

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

    def form_valid(self, form):
        # return CreateView.form_valid(self, form)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = form.cleaned_data.get('email')
            user.is_active = False
            user.save()
            # create profile
            Profile(user=user).save()

            # send validate email

            # collect site name
            site_name = get_current_site(self.request)
            # todo: change hard code subject
            subject = 'Activate account'

            # generate message
            print(urlsafe_base64_encode(force_bytes(user.pk)))
            message = render_to_string('app/account_activation_email.html', {
                'user': user,
                'domain': site_name.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode("utf-8"),
                'token': account_activation_token.make_token(user),
            })

            # here username is email
            email_address = user.username

            # create email
            email = EmailMessage(
                subject, message, to=[email_address]
            )

            # send email
            try:
                email.send()
            except SMTPException as e:
                # todo: need to handle exception if email not send
                pass

        return super(RegisterView, self).form_valid(form)


class SubsriptionView(TemplateView):
    template_name = 'app/subscription.html'


class ProfileView(TemplateView):
    template_name = 'app/profile.html'


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
            profile = user.profile
            if profile.day_to_live <= 0:
                membership_type, created = MembershipType.objects.get_or_create(name='Free')
                membership = Membership(user=user, membership_type=membership_type)
                membership.save()
                membership.membership_type.add(membership_type)
                profile.day_to_live = membership_type.day_to_live
            return HttpResponseRedirect(reverse('home'))
        else:
            return render(request, self.template_name)
