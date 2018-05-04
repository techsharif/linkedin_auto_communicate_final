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


class ProfileSettingsForm(object):
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')
    password = forms.CharField(max_length=32, widget=forms.PasswordInput)
    enable_proxy = forms.BooleanField()
    proxy_address = forms.CharField(max_length=60)
    proxy_authentication_type = forms.CharField(max_length=254)
    proxy_username = forms.CharField(max_length=254)
    proxy_password = forms.CharField(max_length=254)
    license_type = forms.CharField(max_length=254)

    class Meta:
        db_table = 'Profile'