from django.contrib import admin

from .models import (Membership, MembershipType,
                     LinkedInUser, BotTask,)
class ProfileAdmin(admin.ModelAdmin):
    pass

    
class MembershipAdmin(admin.ModelAdmin):
    pass
    
class MembershipTypeAdmin(admin.ModelAdmin):
    pass
    
class LinkedInUserAdmin(admin.ModelAdmin):
    pass
    
class BotTaskAdmin(admin.ModelAdmin):
    pass

admin.site.register(Membership, MembershipAdmin)
admin.site.register(MembershipType, MembershipTypeAdmin)
admin.site.register(LinkedInUser, LinkedInUserAdmin)    
admin.site.register(BotTask, BotTaskAdmin)
    
