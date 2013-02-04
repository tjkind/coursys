from django import forms
from django.forms.fields import CharField
from django.forms import ModelForm
import datetime

from grades.models import Activity
from coredata.models import Member
from submissionlock.models import SubmissionLock 

#class SubmissionLockForm(forms.Form):
#    def __init__(self, *args, **kwargs):
#        super(SubmissionLockForm, self).__init__(*args, **kwargs)
#        for item in range(5):
#            self.fields['test_field_%s' % item] = CharField(max_length=255)

class SubmissionLockForm(ModelForm):
    class Meta:
        model = SubmissionLock
        exclude = {'config'}