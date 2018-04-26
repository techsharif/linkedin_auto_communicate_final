# -*- coding: utf-8 -*-
"""
Created on Wed Apr 25 15:33:20 IST 2018

@author: Chetna
"""

# Python imports


# Django imports
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect


# local imports
from messenger.models import Campaign

# @login_required
def messenger_home(request, account_id):
    response = {}
    campaigns = Campaign.objects.all()
    response = {'campaigns': campaigns}
    return render(request, 'messenger/messenger.html', response)


def campaigns(request, account_id):
    response = {}
    if request.method == 'POST':
        data = request.POST
        if data.get('name'):
            name = data.get('name')
            if Campaign.objects.filter(account_id=account_id, title=name).exists():
                response = {
                    'error':'Messenger Campaign name already exists'
                }
            else:
                campaign = Campaign(account_id=account_id, title=name, status='active')
                campaign.save()
                return HttpResponseRedirect("/%s/messenger/"% str(account_id))
        else:
            response = {
                'error':'Messenger Campaign name required'
            }
    else:
        campaigns = Campaign.objects.all()
        response = {'campaigns': campaigns}
    return render(request, 'messenger/campaigns.html', response)


def getcampaigns(request, account_id, campaign_id):
    response = {}
    campaign = Campaign.objects.get(pk=campaign_id)
    response = {
        'campaign': campaign
    }
    return render(request, 'messenger/campaign.html', response)
