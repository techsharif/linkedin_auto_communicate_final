from django import forms


class LoginForm(forms.Form):
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')
    password = forms.CharField(max_length=32, widget=forms.PasswordInput)

    # class Meta:
    #     model = 'User'
