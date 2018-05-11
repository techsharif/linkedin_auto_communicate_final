from django.contrib import admin

from .models import Campaign, CampaignStep, Inbox, ChatMessage

class CampaignAdmin(admin.ModelAdmin):
    pass

class InboxAdmin(admin.ModelAdmin):
    pass

class CampaignStepAdmin(admin.ModelAdmin):
    pass

class ChatMessageAdmin(admin.ModelAdmin):
    pass

admin.site.register(Campaign, CampaignAdmin)
admin.site.register(CampaignStep, CampaignStepAdmin)
admin.site.register(Inbox, InboxAdmin)
admin.site.register(ChatMessage, ChatMessageAdmin)