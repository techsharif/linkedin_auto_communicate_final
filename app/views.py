from datetime import datetime
from getpass import getpass
import re
import sys
import time

from django.http import HttpResponse
from django.shortcuts import render, redirect
from selenium import webdriver
from selenium.common.exceptions import *
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from . forms import RegisterForm, LoginForm, PinForm, ProfileSettingsForm
from .models import LinkedInUser, Membership


def index(request):
    #if request.session.get('useremail', 'none') == 'none':
    #    return redirect('login')
    return render(request, 'app/home.html')


##############################################################################################################################################

def exist_user():
    try:
        error_span = wait.until(EC.visibility_of_element_located((By.ID, "session_key-login-error")))
        no_exist_user_alert = error_span.text
        print (no_exist_user_alert)
        return False
    except Exception as e:
        return True


def suspended_user():
    pass


def limited_user():
    pass

###############################################################################################################################################

def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user_email = form.cleaned_data.get('email')
            user_password = form.cleaned_data.get('password')
            # remember_me = form.cleaned_data.get('remember')
            if User.objects.filter(email=user_email).exists():
                user_account = User.objects.get(email=user_email)
                password = user_account.password
                if password != user_password:
                    print("---Password incorrect!---") 
                else:
                    print("---Login Successful!---")
                    request.session['useremail'] = user_email

                    if not request.POST.get('remember', None):
                        request.session.set_expiry(0)

                    latest_login_time = datetime.now()
                    User.objects.filter(email=user_email).update(latest_login=latest_login_time)

                    return redirect('index')

            else:
                print("---Unregister User! Please Register!---")
    else:
        form = LoginForm()
    return render(request, 'app/login.html', {'form': form})
            


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user_email = form.cleaned_data.get('email')
            user_password = form.cleaned_data.get('password')
            user_password_confirm = form.cleaned_data.get('confirmpassword')
            if user_password != user_password_confirm:
                print("----Password didn't confirm! Please enter password again.----")
            else:
                # options = Options()
                # options.add_argument('--headless')

                # driver = webdriver.Firefox(options=options)
                driver = webdriver.Firefox(executable_path='D:\SQTechnology\Projects\development\geckodriver.exe')

                driver.get("https://www.linkedin.com")
                wait = WebDriverWait(driver, 2)

                print("------working-----")

                email = wait.until(EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, "input#login-email")))
                print("------pass email---------")

                password = wait.until(EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, "input#login-password")))
                print("------pass password---------")

                signin_button = wait.until(EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, "input#login-submit")))
                print("------pass button---------")

                email.clear()
                password.clear()

                email.send_keys(user_email)
                password.send_keys(user_password)

                signin_button.click()
                print("----------click sign in----------------")

                # check if user is exist
                if exist_user():
                    print("That user is an existing user.")
                    if User.objects.filter(email=user_email).exists():
                        print ("---This user account already exists---")
                        print("--------pin code step----------")
                        # pin code verification
                        try:
                            pincode_input = wait.until(EC.visibility_of_element_located(
                                (By.CSS_SELECTOR, "input#verification-code")))
                            return redirect('pinverify')
                        except Exception as e:
                            print("---sucessfull login without pin code verification!---")
                        # if pincode_input != 'Null':
                        #     return redirect('pinverify')
                        # else:
                        #     print("sucessfull login without pin code verification!")
                    else:
                        latest_login = datetime.now()
                        status = 1
                        user_account = User(email=user_email, password=user_password, latest_login=latest_login, status=status)
                        user_account.save()

                        user_account = User.objects.get(email=user_email)
                        account_id = user_account.id

                        user_profile = Profile(
                            account_id=account_id,
                            enable_proxy=0,
                            proxy_address=None,
                            proxy_authentication_type=0,
                            proxy_username=None,
                            proxy_password=None,
                            license_type=0
                        )
                        user_profile.save()
                        print("----------Profile save--------")


                        print("----Saved user-----")

                    return redirect('login')
                else:
                    print("---That user is not exist in Linkedin.---")
    else:
        form = RegisterForm()
    return render(request, 'app/register.html', {'form': form})


def pinverify(request):
    if request.method == 'POST':
        form = PinForm(request.POST)
        if form.is_valid():
            pincode = form.cleaned_data.get(pincode)
            pin_input_box = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "input#verification-code")))
            pin_submit_btn = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "input#btn-primary")))
            pin_input_box.clear()
            pin_input_box.send_keys(pincode)
            pin_submit_btn.click()
    else:
        form = PinForm()
    return render(request, 'app/pinverify.html', {'form': form})


def logout(request):
    try:
        del request.session['useremail']
    except KeyError:
        pass
    return redirect('login')


def update_account(request):
    form = ProfileSettingsForm(request.POST)
    user_email = request.session['useremail']
    user_account = User.objects.get(email=user_email)
    account_id = user_account.id
    user_password = user_account.password
    
    if Profile.objects.filter(account_id=account_id).exists():
        user_profile = Profile.objects.get(account_id=account_id)
        enable_proxy = user_profile.enable_proxy
        proxy_address = user_profile.proxy_address
        proxy_authentication_type = user_profile.proxy_authentication_type
        proxy_username = user_profile.proxy_username
        proxy_password = user_profile.proxy_password
        license_type = user_profile.license_type

        return render(request, 'app/account_form.html', {'email': user_email, 'password': user_password, 'enable_proxy': enable_proxy, 'proxy_address': proxy_address, 'proxy_authentication_type': proxy_authentication_type, 'proxy_username': proxy_username, 'proxy_password': proxy_password, 'license_type': license_type})

    else:
        form = ProfileSettingsForm()
    return render(request, 'app/account_form.html', {'form': form, 'email': user_email, 'password': user_password})



def account(request):
    user_email = request.session['useremail']
    user_account = User.objects.get(email=user_email)
    account_id = user_account.id
    user_password = user_account.password
    form = ProfileSettingsForm()

    if Profile.objects.filter(account_id=account_id).exists():
        print("-------Exists--------------")
        user_profile = Profile.objects.get(account_id=account_id)
        enable_proxy = user_profile.enable_proxy
        proxy_address = user_profile.proxy_address
        proxy_authentication_type = user_profile.proxy_authentication_type
        proxy_username = user_profile.proxy_username
        proxy_password = user_profile.proxy_password
        license_type = user_profile.license_type

        if request.method == 'POST':
            print("-------------submit-------------")
            form = ProfileSettingsForm(request.POST)
            if form.is_valid():
                print("-----form valid---------")
                enable_proxy = form.cleaned_data.get('enable_proxy')
                proxy_address = form.cleaned_data.get('proxy_address')
                proxy_authentication_type = form.cleaned_data.get('proxy_authentication_type')
                proxy_username = form.cleaned_data.get('proxy_username')
                proxy_password = form.cleaned_data.get('proxy_password')
                license_type = form.cleaned_data.get('license_type')

                Profile.objects.filter(account_id=account_id).update(
                    enable_proxy=enable_proxy,
                    proxy_address=proxy_address,
                    proxy_authentication_type=proxy_authentication_type,
                    proxy_username=proxy_username,
                    proxy_password=proxy_password,
                    license_type=license_type)
                print("------Profile save---------")
                
                return redirect('index')
            return render(request, 'app/account_form.html', {'form': form, 'email': user_email, 'password': user_password})

        else:
            print("-------No submit------------")
            return render(request, 'app/account_form.html', {
                'form': form,
                'email': user_email,
                'password': user_password,
                'enable_proxy': enable_proxy,
                'proxy_address': proxy_address,
                'proxy_authentication_type': proxy_authentication_type,
                'proxy_username': proxy_username,
                'proxy_password': proxy_password,
                'license_type': license_type
            })
    else:
        form = ProfileSettingsForm()
    return render(request, 'app/account_form.html', {'form': form, 'email': user_email, 'password': user_password})

    
