from django.contrib import admin

from .models import Search, SearchResult, TaskQueue

class SearchAdmin(admin.ModelAdmin):
    pass

class TaskQueueAdmin(admin.ModelAdmin):
    pass

class SearchResultAdmin(admin.ModelAdmin):
    pass

admin.site.register(Search, SearchAdmin)
admin.site.register(SearchResult, SearchResultAdmin)
admin.site.register(TaskQueue, TaskQueueAdmin)
