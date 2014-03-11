from django.shortcuts import render
from django.views.generic import TemplateView, ListView
# Create your views here.

__all__=[
    'IssuesIndexView',
    'ProjectCreateView',
]

class IssuesIndexView(TemplateView):
    template_name = 'issues/issues_index.html'

class ProjectCreateView(TemplateView):
    template_name = 'issues/project_form.html'