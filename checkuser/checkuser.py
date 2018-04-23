"""
    require: python 2.7, selenium module, webdriver

"""

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


def exist_user():
    try:
        error_span = wait.until(EC.visibility_of_element_located((By.ID, "session_key-login-error")))
        no_exist_user_alert = error_span.text
        print (no_exist_user_alert)
        return False
    except Exception as e:
        login_success_desc = 'Login successful! that is an existing user.'
        print(login_success_desc)
        return True


def suspended_user():
    pass
    # suspended_account = driver.findElement(By.xpath("//*[contains(.,'account suspended')]"))
    # if (suspended_account == null):
    #     return False
    # else:
    #     return True

def limited_user():
    pass
    # restricted_account = driver.findElement(By.xpath("//*[contains(.,'temporarily restricted')]"))
    # if (restricted_account == null):
    #     return False
    # else:
    #     return True


if __name__ == '__main__':
    
    user_email = raw_input("Enter email address:")
    user_password = getpass("Enter password:")

    options = Options()
    options.add_argument('--headless')

    driver = webdriver.Firefox(options=options)
    driver.get("https://www.linkedin.com")
    wait = WebDriverWait(driver, 5)

    print("----working-----")

    email = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "input#login-email")))
    print("------pass email---------")

    password = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "input#login-password")))
    print("------pass password---------")

    signin_button = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "input#login-submit")))
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
    else:
        print("That user is not exist in Linkedin.")

    # # check if user is suspended
    # if suspended_user():
    #     print("That user is suspended.")
    # else:
    #     print("That user is not suspended.")

    # # check if user is has any limitation
    # if limited_user():
    #     print("That user has been restricted.")
    # else:
    #     print("Thank user is not restricted.")
