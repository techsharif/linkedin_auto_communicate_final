# -*- coding: utf-8 -*-
"""
Created on Wed Apr 25 15:33:20 IST 2018

@author: Chetna
"""

# Python imports


# Django imports
import json

from django.contrib.auth.decorators import login_required
#from django.http import HttpResponseRedirect
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
#from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.generic.base import View

from .models import Inbox, ContactStatus, Campaign
from django.db import transaction


# local imports
decorators = (never_cache, login_required,)


class AjaxHttpResponse(object):
    payload = dict(ok=True)
    def AjaxResponse(self, payload=None):
        if payload is None:
            payload = self.payload
            
        json_data = json.dumps(payload)
        return HttpResponse(json_data, content_type='application/json')

@method_decorator(decorators, name='dispatch')
class ContactStatusView(View):
    def get(self, request, pk):
        contact = get_object_or_404(Inbox, pk=pk)
        new_status = request.GET.get('status', None)
        if new_status is None or ContactStatus.valid_status(new_status):
            raise Exception("Invalid status")
        
        contact.status = new_status
        contact.save
        json_data = json.dumps(dict(ok=True))
        return HttpResponse(json_data, content_type='application/json')
        
@method_decorator(decorators, name='dispatch')        
class CampaignContactsView(AjaxHttpResponse, View):
    def post(self, request):
        data = request.POST
        campaign_id = data.get('campaign')
        campaign = get_object_or_404(Campaign, pk=campaign_id)
        with transaction.atomic():
            campaign.contacts.clear()
            cids = data.get('cid').split(',')
            for cid in cids:
                contact = get_object_or_404(Inbox, pk=cid)
                contact.status = ContactStatus.IN_QUEUE_N
                contact.save()
                campaign.contacts.add(contact)
                
        
        return self.AjaxResponse()