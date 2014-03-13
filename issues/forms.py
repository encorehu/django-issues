from django import forms
from django.contrib.auth.models import User
from django.forms.fields import IntegerField
from django.forms.models import modelformset_factory, BaseModelFormSet
from django.contrib.auth.models import User

from issues.models import Project
from issues.models import Milestone
from issues.models import Issue,Urgency, Importance, ISSUE_STATUS_CHOICES


class MilestoneCreateForm(forms.ModelForm):
    class Meta:
        model = Milestone
        exclude = ('date_completed',)


class ProjectForm(forms.ModelForm):
    """
    ModelForm for a Project, used for creation and editing
    """
    title = forms.CharField(min_length=3, max_length=50)
    alias = forms.CharField(min_length=2, max_length=8, required=False)
    msg   = forms.CharField(max_length=255, required=False,help_text='please input the reason of modify')

    class Meta:
        model = Project
        exclude = ('members', )

class MemberQuickAdd(forms.Form):
    user = forms.CharField()

    def clean_user(self):
        username = self.cleaned_data['user']
        try:
            user = User.objects.get(username=username)
            return user
        except User.DoesNotExist:
            raise forms.ValidationError(u'That user does not exist')


class IssueCreateForm(forms.ModelForm):
    """
    ModelForm for an Issue, used for creation and editing
    """
    class Meta:
        model = Issue
        fields = ('summary', 'description',)

class IssueEditForm(forms.ModelForm):


    owners = forms.CharField(help_text=u"Enter valid usernames for members of this project, separated by commas", required=False)
    #status = forms.ChoiceField()
    msg = forms.CharField(max_length=100, required=False,help_text='please input the reason of modify')

    def __init__(self, *args, **kwargs):
        super(IssueEditForm, self).__init__(*args, **kwargs)
        self.initial['owners'] = ','.join([u.username for u in self.instance.owners.all()])
        #if self.instance.project.has_issue_status:
        #    my_choices = []
        #    for x in self.instance.project.issue_status.split(','):
        #        my_choices.append((x,x))
        #    self.fields['status'].choices = tuple(my_choices)
        #    self.fields['status'].widget.choices = tuple(my_choices)

    def clean_owners(self):
        data = self.cleaned_data['owners']
        if data == u'':
            return data
        usernames = [username.strip() for username in data.split(',')]
        invalid_usernames = []
        print usernames
        users = []
        for username in usernames:
            user = self.instance.project.members.filter(username=username)
            if not user:
                invalid_usernames.append(username)
            else:
                users.append(user[0])
        print users
        print invalid_usernames
        if invalid_usernames:
            if len(invalid_usernames) > 1:
                raise forms.ValidationError("%s are invalid usernames" % ','.join(invalid_usernames))
            else:
                raise forms.ValidationError("%s is not an invalid username of your project members" % invalid_usernames[0])
        return users

    def clean_msg(self):
        data = self.cleaned_data['msg']

        if not data:
            #raise forms.ValidationError("msg is empty")
            data = 'UPDATED' # DO NOT MODIFY THIS WORD!
        return data

    class Meta:
        model = Issue

class SearchForm(forms.Form):
    """
    Allows user to search for Issues based on certain criteria, none required, most found in Issue model
    """
    keywords = forms.CharField(help_text='Keyword search of issue title and description', required=False)
    date_added = forms.DateTimeField(help_text='Date issue was created', required=False)
    date_modified = forms.DateTimeField(help_text='Date issue was last modified', required=False)
    date_completed = forms.DateTimeField(help_text='Date issue was closed', required=False)
    date_due = forms.DateTimeField(help_text='Date issue is due', required=False)
    status = forms.ChoiceField(choices=ISSUE_STATUS_CHOICES, required=False)
    urgency = forms.ModelChoiceField(queryset=Urgency.objects.all(), required=False)
    importance = forms.ModelChoiceField(queryset=Importance.objects.all(), required=False)
    creator = forms.ModelChoiceField(queryset=User.objects.all(), required=False)
    owner = forms.ModelChoiceField(queryset=User.objects.all(), required=False)
    stakeholder = forms.ModelChoiceField(queryset=User.objects.all(), required=False)

class BaseIssueFormSet(BaseModelFormSet):
    def add_fields(self, form, index):
        """Add a NON-hidden field for the object's primary key."""
        from django.db.models import AutoField
        self._pk_field = pk = self.model._meta.pk
        if pk.auto_created or isinstance(pk, AutoField):
            form.fields[self._pk_field.name] = IntegerField(required=False)
        super(BaseModelFormSet, self).add_fields(form, index)

IssueFormSet = modelformset_factory(Issue, formset=BaseIssueFormSet, can_delete=True)
