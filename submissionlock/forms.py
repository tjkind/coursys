from django import forms
from django.forms.fields import CharField, ChoiceField
import datetime

from grades.models import Activity
from coredata.models import Member
from submissionlock.models import SubmissionLock 

LOCK_CHOICES = (
        ('1', 'Locked'),
        ('0', 'Unlocked'),
    )

class SubmissionLockForm(forms.Form):
    def __init__(self, students, activity, *args, **kwargs):
        super(SubmissionLockForm, self).__init__(*args, **kwargs)
        current_time = datetime.datetime.now()
        for member in students:
            try:
                student_lock = SubmissionLock.objects.get(activity=activity, member=student)
                if student_lock.effective_date > current_time:
                    self.fields["%s" % (member.person.userid)]=ChoiceField(LOCK_CHOICES, initial='1')
                else:
                    self.fields["%s" % (member.person.userid)]=ChoiceField(LOCK_CHOICES, initial='0')
            except:
                self.fields["%s" % (member.person.userid)]=ChoiceField(LOCK_CHOICES, initial='0')
    
    def clean(self):
        cleaned_data = self.cleaned_data
        for student in students:
            member = Member.objects.filter(__person__userid = student.person.userid)
            lock_status = cleaned_data.get("%s" % student)
            
        return cleaned_data