from django.conf.urls import patterns, include, url

from .views import *

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'issues.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    #url(r'^$',
    #    IssuesIndexView.as_view(),
    #    name='issues_index'),


    url(r'^$',
        ProjectListView.as_view(),
        name='project_list'),

    url(r'^create/$',
        ProjectCreateView.as_view(),
        name='create_project'),

    url(r'^(?P<project_slug>[-\w]+)/$',
        ProjectDetailView.as_view(),
        name='project_detail'),

    url(r'^(?P<project_slug>[-\w]+)/members/$',
        MembershipListView.as_view(),
        name='member_list'),

    url(r'^(?P<project_slug>[-\w]+)/members/add/$',
        MembershipCreateView.as_view(),
        name='add_members'),


    url(r'^(?P<project_slug>[-\w]+)/issues/$',
        IssueListView.as_view(),
        name='issue_list'),

    url(r'^(?P<project_slug>[-\w]+)/issues/create/$',
        IssueCreateView.as_view(),
        name='create_issue'),

    url(r'^(?P<project_slug>[-\w]+)/issues/(?P<issue_id>\d+)/$',
        IssueDetailView.as_view(),
        name='issue_detail'),

    url(r'^(?P<project_slug>[-\w]+)/issues/(?P<issue_id>\d+)/edit/$',
        IssueUpdateView.as_view(),
        name='issue_edit'),

    url(r'^(?P<project_slug>[-\w]+)/issues/search/$',
        IssuesSearchView.as_view(),
        name='issues_search'),

    url(r'^(?P<project_slug>[-\w]+)/issues/attachment/(?P<key>\d+)/$',
        AttachmentDetailView.as_view(),
        ),

    #url(r'^triage/$',
    #    TriageView.as_view(),
    #    name='issues_triage'),

    url(r'^(?P<project_slug>[-\w]+)/milestone/$',
        MilestoneListView.as_view(),
        name='milestone_list'),

    url(r'^(?P<project_slug>[-\w]+)/milestone/create/$',
        MilestoneCreateView.as_view(),
        name='create_milestone'),

    url(r'^(?P<project_slug>[-\w]+)/milestone/(?P<milestone_id>\d+)/$',
        MilestoneDetailView.as_view(),
        name='milestone_detail'),

    url(r'^(?P<project_slug>[-\w]+)/timeline/$',
        TimeLineListView.as_view(),
        name='timeline_list'),


)
