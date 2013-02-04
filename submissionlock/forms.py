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
    def __init__(self, students, locked_students, *args, **kwargs):
        super(SubmissionLockForm, self).__init__(*args, **kwargs)
        for student in students:
            if student in locked_students:
                self.fields["%s" % (student.person.userid)] = ChoiceField(LOCK_CHOICES, initial = True)
            else:
                self.fields["%s" % (student.person.userid)] = ChoiceField(LOCK_CHOICES, initial = False)
    
    def clean(self):
        cleaned_data = self.cleaned_data
        for student in students:
            member = Member.objects.filter(__person__userid = student.person.userid)
            lock_status = cleaned_data.get("%s" % student)
            
        return cleaned_data