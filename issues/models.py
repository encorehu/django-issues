from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from django.template.defaultfilters import slugify
import datetime
from django.utils import timezone

ISSUE_ALIAS  = _('Issue')
ISSUE_STATUS = _('new,wontfix,duplicate,accepted,inprogress,resolved,review,other')
class Project(models.Model):
    title       = models.CharField(max_length=50)
    slug        = models.SlugField(unique=True)
    description = models.TextField(null=True, blank=True)
    url         = models.URLField(blank=True)
    private     = models.BooleanField(default=False)

    members     = models.ManyToManyField(User, through="Membership")
    creator     = models.ForeignKey(User, related_name='created_projects', editable=False)
    watchers    = models.ManyToManyField(User, blank=True, null=True,
		                                 related_name='watchers')
    issue_alias = models.CharField(max_length=8,  blank=True, default=ISSUE_ALIAS)
    issue_status = models.CharField(max_length=100, blank=True, default=ISSUE_STATUS)

    date_added    = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.title

    def has_issue_status(self):
        # not equal ISSUE_STATUS, return True, if diffrent from the default
        return self.issue_status != ISSUE_STATUS

    def save(self, **kwargs):
        if self.slug is None:
            self.slug = slugify(self.title)
            self.slug = self.slug.lower().replace('-','_')
            self.slug = self.slug.lower()

        if not self.issue_alias:
            self.issue_alias  = ISSUE_ALIAS

        if not self.issue_status:
            self.issue_status = ISSUE_STATUS

        return super(Project,self).save(**kwargs)
        #if self.id is None:
        #    self.slug = slugify(self.title)
        #return super(Project, self).save()

    @models.permalink
    def get_absolute_url(self):
        return ('project_detail', (), {'project_slug':self.slug})

    @property
    def project(self):
        return self

class Membership(models.Model):
    user      = models.ForeignKey(User)
    project   = models.ForeignKey(Project)
    joined_at = models.DateTimeField(auto_now_add=True)
