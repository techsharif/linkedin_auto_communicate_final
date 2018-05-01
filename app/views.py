from django.http import HttpResponse
from django.shortcuts import render, redirect
from . forms import LoginForm,PinForm
from . models import User

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import *
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options

from getpass import getpass
import sys
import re
import time


def index(request):
    return render(request, 'app/index.html')


def account(request):
    return render(request, 'app/account.html')


# def signup(request):
#     if request.method == 'POST':
#         form = SignUpForm(request.POST)
#         if form.is_valid():
#             form.save()
#             username = form.cleaned_data.get('username')
#             raw_password = form.cleaned_data.get('password1')
#             user = authenticate(username=username, password=raw_password)
#             login(request, user)
#             return redirect('index')
#     else:
#         form = SignUpForm()
#     return render(request, 'app/signup.html', {'form': form})


#############################################################################

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


# def pinverify():
#     try:
#         pin_input_box = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "input#verification-code")))
#         pin_submit_btn = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "input#btn-primary")))
#         print("Please check your email address to verify.....")
#         pincode = raw_input("Enter pin code:")
#         pin_input_box.clear()
#         pin_input_box.send_keys(pincode)
#         pin_submit_btn.click()
#         return True
#     except Exception as e:
#         return False

#############################################################################


def login(request):
    global driver
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user_email = form.cleaned_data.get('email')
            user_password = form.cleaned_data.get('password')

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
                    print ("This user account already exists")
                    print("--------pin code step----------")
                    # pin code verification
                    try:
                        pincode_input = wait.until(EC.visibility_of_element_located(
                            (By.CSS_SELECTOR, "input#verification-code")))
                        return redirect('pinverify')
                    except Exception as e:
                        print("sucessfull login without pin code verification!")
                    # if pincode_input != 'Null':
                    #     return redirect('pinverify')
                    # else:
                    #     print("sucessfull login without pin code verification!")
                else:
                    user_account = User(email=user_email, password=user_password)
                    user_account.save()

                return redirect('index')
            else:
                print("That user is not exist in Linkedin.")        
    else:
        form = LoginForm()
    return render(request, 'app/login.html', {'form': form})


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


def logout():
    return render(request, 'app/login.html', {'form': form})
