from django import forms


class CreateCampaignForm(forms.Form):
    name = forms.CharField(required=True, widget=forms.TextInput)
    # setps = forms.ChoiceField(widget=forms.Select(attrs={'class':'selector'}))
