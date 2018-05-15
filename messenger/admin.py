from django.contrib import admin

from .models import Campaign, CampaignStep, Inbox, ChatMessage

class CampaignAdmin(admin.ModelAdmin):
    pass

class InboxAdmin(admin.ModelAdmin):
    list_display = ('id', 'owner', 'status', 'name', 'company', 'title', 'latest_activity',) 
    list_filter = ('status', 'owner')

class CampaignStepAdmin(admin.ModelAdmin):
    pass

class ChatMessageAdmin(admin.ModelAdmin):
    pass

admin.site.register(Campaign, CampaignAdmin)
admin.site.register(CampaignStep, CampaignStepAdmin)
admin.site.register(Inbox, InboxAdmin)
admin.site.register(ChatMessage, ChatMessageAdmin)