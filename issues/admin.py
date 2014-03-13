from django.contrib import admin
from issues.models import Project
from issues.models import Issue
from issues.models import TimeLine,Milestone

class IssueAdmin(admin.ModelAdmin):
    list_display = ('summary',)
    list_filter = ('status', 'priority')
    search_field = ['^summary',]
    raw_id_fields = ('owners', )

    def save_model(self, request, obj, form, change):
        if not change:
            obj.creator = request.user

        obj.save()

class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title','date_added')
    search_field = ['^title',]
    raw_id_fields = ('watchers', )

    def save_model(self, request, obj, form, change):
        obj.creator = request.user
        obj.save()

admin.site.register(TimeLine)
admin.site.register(Milestone)
admin.site.register(Project,ProjectAdmin)
admin.site.register(Issue, IssueAdmin)
