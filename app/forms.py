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
