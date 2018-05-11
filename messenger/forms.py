from django import forms
from django.utils.translation import gettext_lazy as _


from messenger.models import Campaign

css_form_attrs = {'class': 'form-control'}

class CreateCampaignForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        is_bulk = kwargs.pop('is_bulk', False)
        owner_id = kwargs.pop('owner_id', None)
        super(CreateCampaignForm, self).__init__(*args, **kwargs)
        if owner_id:
            self.fields['copy_campaign'].queryset = Campaign.objects.filter(
                owner_id=owner_id, is_bulk=is_bulk)
        else:
            self.fields['copy_campaign'].queryset = Campaign.objects.filter(
                is_bulk=is_bulk)
        
    title = forms.CharField(
        label=_('Connector Campaign name'),
        widget=forms.TextInput(
            attrs=css_form_attrs)
        )
    
    copy_campaign = forms.ModelChoiceField(
        required=False,
        label=_('Copy Connector Campaign steps from'),
        widget=forms.Select(attrs=css_form_attrs),
        queryset=Campaign.objects.all()
        )
    
    class Meta:
        model = Campaign
        fields = ('title', 'copy_campaign', )


class CreateCampaignMesgForm(CreateCampaignForm):
    def __init__(self, *args, **kwargs):
        super(CreateCampaignMesgForm, self).__init__(*args, **kwargs)
        self.fields['title'].label = 'Messenger Campaign name'
        self.fields['copy_campaign'].label = 'Copy Messenger Campaign steps from'