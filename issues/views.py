from django.shortcuts import render, render_to_response
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView
# Create your views here.
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from django.contrib import messages

from issues.forms import IssueCreateForm, IssueEditForm, SearchForm, IssueFormSet
from issues.forms import MilestoneCreateForm
from issues.forms import ProjectForm, MemberQuickAdd

from issues.models import timeline_updater,ISSUE_STATUS
from issues.signals import post_save

from .models import *
from .forms import *
#__all__=[
#    'IssuesIndexView',
#    'ProjectCreateView',
#]

class LoginRequiredMixin(object):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(*args, **kwargs)

class IssuesIndexView(TemplateView):
    template_name = 'issues/issues_index.html'

class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = 'issues/project_form.html'

    def get_form_kwargs(self):
        kwargs = super(ProjectCreateView, self).get_form_kwargs()
        instance = self.model(creator=self.request.user)
        kwargs.update({'instance': instance})
        return kwargs

    def form_valid(self, form):
        kwargs = {}
        kwargs['instance']   = self.object
        kwargs['created']    = True
        kwargs['msg'] = 'Created Project'
        post_save.send(sender= self.object.__class__, **kwargs)
        member = Membership.objects.create(project=self.object,
                                               user=self.request.user)

        return super(IssueUpdateView,self).form_valid(form)

class ProjectUpdateView(LoginRequiredMixin, UpdateView):
    model = Project

class ProjectListView(ListView):
    model = Project

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated():
            project_list = Project.objects.filter( Q(private=False) | Q(members=user)).distinct()
        else:
            project_list = Project.objects.filter(private=False)

        return project_list

class ProjectDetailView(DetailView):
    model = Project
    slug_url_kwarg = 'project_slug'
    template_name = "issues/project_detail.html"

    def get_object(self, queryset=None):
        slug = self.kwargs.get(self.slug_url_kwarg, None)
        return get_object_or_404(Project.objects.all(), slug=slug)


class ProjectMixin(object):
    def get_project(self, project_slug_url_kwarg='project_slug'):
        project = get_object_or_404(Project.objects.all(), slug=self.kwargs.get(project_slug_url_kwarg, None))
        self.project = project
        return project

    def get_context_data(self, **kwargs):
        try:
            project = self.project # may be other func called self.get_project() first somewhere.
        except AttributeError:
            project = self.get_project()

        kw = {
            'project':  project,
        }
        kwargs.update(kw)
        return super(ProjectMixin, self).get_context_data(**kwargs)

class IssueCreateView(LoginRequiredMixin, ProjectMixin, CreateView):
    model = Issue
    form_class = IssueCreateForm
    template_name = 'issues/issue_form.html'

    def dispatch(self, request, *args, **kwargs):
        print 'kwargs', kwargs, self.kwargs
        project = self.get_project()
        print 'project',project
        return super(IssueCreateView, self).dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(IssueCreateView, self).get_form_kwargs()
        print kwargs
        instance = self.model(creator=self.request.user)
        instance.project = self.project
        kwargs.update({'instance': instance})
        return kwargs

    def get_success_url(self):
        return reverse('issue_list', kwargs={'project_slug': self.project.slug})

    def form_valid(self, form):
        redirect = super(IssueUpdateView,self).form_valid(form)
        kwargs = {}
        kwargs['instance']   = self.object
        kwargs['created']    = True
        kwargs['msg'] = 'Created Issue'
        post_save.send(sender= self.object.__class__, **kwargs)
        return redirect

class IssueUpdateView(LoginRequiredMixin, ProjectMixin, UpdateView):
    model = Issue
    pk_url_kwarg = 'issue_id'
    form_class = IssueEditForm
    #success_url = ''
    template_name='issues/issue_detail.html'

    def get_success_url(self):
        return reverse('issue_list', kwargs={'project_slug': self.project.slug})

    def get_form_kwargs(self):
        print 'you call get_form_kwargs'
        project = self.get_project()
        kwargs = super(IssueUpdateView, self).get_form_kwargs()
        if 'instance' not in kwargs: # create
            instance = self.model(creator=self.request.user)
            instance.project = project
            kwargs.update({'instance': instance})
        print kwargs
        return kwargs

    def form_valid(self, form):
        redirect = super(IssueUpdateView,self).form_valid(form)
        kwargs = {}
        kwargs['instance']   = self.object
        kwargs['created']    = False
        kwargs['msg'] = 'Update Issue'
        post_save.send(sender= self.object.__class__, **kwargs)
        return redirect

    def form_invalid(self, form):
        messages.warning(self.request, unicode(form.errors))
        print 'error', unicode(form.errors).encode('gbk')
        return super(IssueUpdateView,self).form_invalid(form)



class IssueListView(ProjectMixin, ListView):
    model = Issue
    slug_url_kwarg = 'project_slug'

    def get_queryset(self):
        project = self.get_project()
        a= project.issues.all()
        return project.issues.all()

    def get_context_data(self, **kwargs):
        context_data = super(IssueListView, self).get_context_data(**kwargs)
        print context_data
        return context_data

class IssueDetailView(ProjectMixin, DetailView):
    model = Issue
    pk_url_kwarg = 'issue_id'

    #def get_object(self):
    #    slug = self.kwargs.get(self.slug_url_kwarg, None)
    #    return get_object_or_404(Project.objects.all(), slug=self.kwargs.get(kwargs['project_slug'], None))



class IssuesSearchView(ListView, ProjectMixin):
    model = Issue


class MilestoneCreateView(LoginRequiredMixin, ProjectMixin, CreateView):
    model = Milestone

    def get_form_kwargs(self):
        kwargs = super(MilestoneCreateView, self).get_form_kwargs()
        print kwargs
        instance = self.model()
        instance.project = self.get_project()
        kwargs.update({'instance': instance})
        return kwargs

class MilestoneUpdateView(LoginRequiredMixin, ProjectMixin, UpdateView):
    model = Milestone

class MilestoneListView(ProjectMixin, ListView):
    model = Milestone

class MilestoneDetailView(ProjectMixin, DetailView):
    model = Milestone


# Membership Views
class MembershipCreateView(LoginRequiredMixin, ProjectMixin, CreateView):
    model = Membership


class MembershipUpdateView(LoginRequiredMixin, ProjectMixin, UpdateView):
    model = Membership

class MembershipListView(ProjectMixin, ListView):
    model = Membership

class MembershipDetailView(ProjectMixin, DetailView):
    model = Membership


class TimeLineCreateView(LoginRequiredMixin, ProjectMixin, CreateView):
    model = TimeLine

class TimeLineUpdateView(LoginRequiredMixin, ProjectMixin, UpdateView):
    model = TimeLine

class TimeLineListView(ProjectMixin, ListView):
    model = TimeLine

    def get_queryset(self):
        project = self.get_project()
        queryset = project.timeline_set.all()
        return queryset

class TimeLineDetailView(ProjectMixin, DetailView):
    model = TimeLine

# Attachment Views
class AttachmentCreateView(LoginRequiredMixin, ProjectMixin, CreateView):
    model = Attachment

class AttachmentUpdateView(LoginRequiredMixin, ProjectMixin, UpdateView):
    model = Attachment

class AttachmentListView(ProjectMixin, ListView):
    model = Attachment

class AttachmentDetailView(ProjectMixin, DetailView):
    model = Attachment
