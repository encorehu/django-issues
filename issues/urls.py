from django.conf.urls import patterns, include, url

from .views import *

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'issues.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^$', IssuesIndexView.as_view(), name='issues_index'),
)
