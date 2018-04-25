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


@login_required
def messenger_home(request):
    return render(request, 'messenger/messenger.html')
