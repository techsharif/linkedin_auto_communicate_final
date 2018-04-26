# -*- coding: utf-8 -*-
"""
Created on Wed Apr 25 15:33:20 IST 2018

@author: Chetna
"""

# Python imports


# Django imports
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required


# local imports
from messenger.models import Campaign

# @login_required
def messenger_home(request, account_id):
    response = {}
    campaigns = Campaign.objects.all()
    response = {'campaigns': campaigns}
    return render(request, 'messenger/messenger.html', response)
