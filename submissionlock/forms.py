from django import forms
from django.forms.fields import CharField, ChoiceField
import datetime

from grades.models import Activity
from coredata.models import Member
from submissionlock.models import SubmissionLock 

LOCK_CHOICES = (
        (True, 'Locked'),
        (False, 'Unlocked'),
    )

class SubmissionLockForm(forms.Form):
    def __init__(self, students, *args, **kwargs):
        super(SubmissionLockForm, self).__init__(*args, **kwargs)
        for student in students:
            #self.fields['test_field_%s' % item] = CharField(max_length=255)
            self.fields["%s    %s" % (student.person.userid, student.person.emplid)] = ChoiceField(LOCK_CHOICES)