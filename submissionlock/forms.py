from django import forms
import datetime

from grades.models import Activity
from coredata.models import Member
from submissionlock.models import SubmissionLock 

class SubmissionLockForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(SubmissionLockForm, self).__init__(*args, **kwargs)