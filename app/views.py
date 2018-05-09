
from django.contrib.auth import get_user_model
from django.urls.base import reverse_lazy
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView

from app.forms import UserRegisterForm
from app.models import MembershipType


User = get_user_model()
class HomeView(TemplateView):
    template_name = 'app/home.html'
    
    def get_context_data(self, **kwargs):
        ctx = super(HomeView, self).get_context_data(**kwargs)
        for x in MembershipType.objects.all():
            ctx[x.name] = x
        #print('ctx:', ctx)
        return ctx
    

class RegisterView(CreateView):
    form_class = UserRegisterForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('register_done')
    
    def form_valid(self, form):
        #return CreateView.form_valid(self, form)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = form.cleaned_data.get('email')
            user.is_active = False
            user.save()
            # send validate email
        
        return super(RegisterView, self).form_valid(form)

        
        
    
class SubsriptionView(TemplateView):
    template_name = 'app/subscription.html'

    
class ProfileView(TemplateView):
    template_name = 'app/profile.html'

