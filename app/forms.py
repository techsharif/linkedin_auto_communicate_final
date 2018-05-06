from django import forms


class RegisterForm(forms.Form):
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')
    password = forms.CharField(max_length=32, widget=forms.PasswordInput)
    confirmpassword = forms.CharField(max_length=32, widget=forms.PasswordInput)


class LoginForm(forms.Form):
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')
    password = forms.CharField(max_length=32, widget=forms.PasswordInput)
        

class PinForm(forms.Form):
    pincode = forms.CharField(max_length=6)


class ProfileSettingsForm(forms.Form):
    email = forms.EmailField(max_length=254, label='Email')
    password = forms.CharField(max_length=32, widget=forms.PasswordInput, label='Password')
    enable_proxy = forms.BooleanField(widget=forms.CheckboxInput, label='Enable Proxy')
    proxy_address = forms.CharField(max_length=60, widget=forms.TextInput, label='Proxy Address')
    proxy_auth_type_choices = (
        ('0', '(none)'),
        ('1', 'Plain Text Authentication'),
        ('2', 'Basic Authentication Type'),
    )
    proxy_authentication_type = forms.ChoiceField(choices=proxy_auth_type_choices, label='Proxy Authentication Type')
    proxy_username = forms.CharField(max_length=254, label='Proxy Username')
    proxy_password = forms.CharField(max_length=254, widget=forms.PasswordInput, label='Proxy Password')
    license_type_choices = (
        ('0', '14-days Free Trial Basic Subscription Plan'),
        ('1', 'Basic Subscription Plan'),
        ('2', 'Pro Subscription Plan w/Sales Navigator'),
    )
    license_type = forms.ChoiceField(choices=license_type_choices, label='License Type')


