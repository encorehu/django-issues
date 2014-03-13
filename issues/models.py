# -*- coding: utf-8 -*-

import datetime

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.template.defaultfilters import slugify
from django.utils import timezone

from issues import signals

class TimeLine(models.Model):
    project        = models.ForeignKey('Project', editable=False)
    description    = models.TextField()
    date           = models.DateTimeField(auto_now_add=True)
    content_type   = models.ForeignKey(ContentType)
    object_id      = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey()

    def __unicode__(self):
        return self.description

    class Meta:
        ordering = ('-date',)

def timeline_updater(sender, **kwargs):
    #print kwargs
    instance = kwargs['instance']
    project = instance.project

    if 'created' in kwargs and kwargs['created']:
        msg = 'Created '
    else:
        msg = 'Updated '
    description='%s %s' % (msg, sender.__name__)

    if 'msg' in kwargs and kwargs['msg']:
        description = kwargs['msg']

    TimeLine.objects.create(project=project,
                            description=description,
                            content_object=instance)

class Milestone(models.Model):
    project = models.ForeignKey('Project', editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    date_due = models.DateTimeField(null=True, blank=True)
    date_completed = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-date_due',]

    def __unicode__(self):
        return self.title

    @models.permalink
    def get_absolute_url(self):
        return ('milestone_detail', [self.project.slug, str(self.id)])

# Signals
signals.post_save.connect(timeline_updater, sender=Milestone)




ISSUE_ALIAS  = _('Issue')
#ISSUE_STATUS = _('new,wontfix,duplicate,accepted,inprogress,resolved,review,other')
ISSUE_STATUS = u'新问题,不处理,重复问题,已受理,处理中,已解决,待复查,其他'
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

    events        = generic.GenericRelation(TimeLine, related_name='projects')
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

    def percent_finished(self):
        finished = self.issues.filter(finished=True).count()
        allcount = self.issues.count()
        if allcount>0:
            return 100*float(finished)/allcount
        else:
            return 0.0

class Membership(models.Model):
    user      = models.ForeignKey(User)
    project   = models.ForeignKey(Project)
    joined_at = models.DateTimeField(auto_now_add=True)

# Signals
signals.post_save.connect(timeline_updater, sender=Project)



#__all__ = ('Issue', 'Urgency', 'Importance', 'STATUS_CHOICES',)

#ISSUE_STATUS = _('new,wontfix,duplicate,accepted,inprogress,resolved,review,other')

ISSUE_STATUS_CHOICES = (
    ('0', _('New')),
    ('1', _("Won't Fix")),
    ('2', _('Duplicate')),
    ('3', _('Accepted')),
    ('4', _('InProgress')),
    ('5', _('Resolved')),
    ('6', _('AwaitingReview')),
    ('7', _('Other')),
)

ISSUE_PRIORITIY_CHOICES = (
	(1, _('Low')),
	(2, _('Normal')),
	(3, _('High')),
	(4, _('Urgent')),
	(5, _('Immediate')),
)


ATTACHMENT_STATUS_CHOICES= (
    ('current', 'Current'),
    ('superseded', 'Superseded'),
    ('irrelevant', 'No Longer Relevant'),
)
class Urgency(models.Model):
    title = models.CharField(max_length=35, unique=True)
    order = models.IntegerField(default=1)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = u"Levels of Urgency"
        verbose_name = u"Level of Urgency"
        ordering = ['order', 'title']

    def __unicode__(self):
        return self.title

    @models.permalink
    def get_absolute_url(self):
        return ('issues.views.urgency', [str(self.id)])

class Importance(models.Model):
    title = models.CharField(max_length=35, unique=True)
    order = models.IntegerField(default=1)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = u"Levels of Importance"
        verbose_name = u"Level of Importance"
        ordering = ['order', 'title']

    def __unicode__(self):
        return self.title

    @models.permalink
    def get_absolute_url(self):
        return ('issues.views.importance', [str(self.id)])


class Issue(models.Model):

    project       = models.ForeignKey(Project, related_name='issues', editable=False)
    summary       = models.CharField(max_length=255)
    description   = models.TextField()
    date_added    = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    date_due      = models.DateTimeField(null=True, blank=True)
    milestone     = models.ForeignKey(Milestone, null=True, blank=True)
    creator       = models.ForeignKey(User, related_name="created_issues", editable=False)
    owners        = models.ManyToManyField(User, related_name="assigned_issues", null=True, blank=True)
    status        = models.CharField(max_length=10, choices=ISSUE_STATUS_CHOICES, default='0')
    finished      = models.BooleanField(default=False)
    priority      = models.IntegerField(_('priority'), choices=ISSUE_PRIORITIY_CHOICES, blank=True, null=True, default=2)
    order         = models.IntegerField(blank=True, null=True, default=0, editable=False)

    class Meta:
        ordering = ['-order', '-id','-date_due']

    def __unicode__(self):
        return u'#%d %s' % (self.order, self.summary)

    @models.permalink
    def get_absolute_url(self):
        return ('issue_detail', [self.project.slug, str(self.id)])

    def save(self, force_insert=False, force_update=False):
        new_issue = False
        first     = 1 # or 0 indexed?

        if not self.id:
            self.date_added  = timezone.now()
            try:
                p1                 = self.project
                latest_issue       = p1.issues.latest('date_added') # get the latest one
                latest_issue_order = latest_issue.order # the thread already exist atleast another post,except this one
                # insert a issue
                if self.order == 0: # if floor == 0, the issue is the first time insert to  issue set
                    self.order = latest_issue_order + 1
                # update a issue
                #elseif order !=0 :# update a exsist issue, save the update data,do not need to update its order number
                #    self.order already >= 1 ,so donot need change
            except Issue.DoesNotExist: # the thread has no post return by the upon progress(inserting)
                self.order = first        # top floor is 1 indexed

        if not self.priority:
            self.priority = 2
        super(Issue, self).save(force_insert, force_update)

class Attachment(models.Model):
    creator    = models.ForeignKey(User, related_name="created_issue_attachments")
    date_added = models.DateTimeField(auto_now_add=True)
    status     = models.CharField(max_length=10, choices=ATTACHMENT_STATUS_CHOICES, default='current')
    attachment = models.FileField(upload_to='attachments/%Y/%m/%d')
    issue      = models.ForeignKey(Issue, related_name="attachments")

    def __unicode__(self):
        return u'Attachment: %s' % self.attachment.name

    @models.permalink
    def get_absolute_url(self):
        return ('issues.views.attachment', [str(self.id)])

# Signals
signals.post_save.connect(timeline_updater, sender=Issue)
