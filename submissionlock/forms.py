from django import forms
from django.conf import settings
from django.forms.fields import CharField, ChoiceField
from django.utils.safestring import mark_safe
import datetime

from grades.models import Activity
from grades.forms import CustomSplitDateTimeWidget
from coredata.models import Member
from submissionlock.models import SubmissionLock, ActivityLock

_required_star = '<span><img src="'+settings.MEDIA_URL+'icons/required_star.gif" alt="required"/></span>'
LOCK_CHOICES = (
        ('lock', 'lock'),
        ('unlock', 'unlock'),
    )

class SubmissionLockForm(forms.Form):
    lock_date = forms.SplitDateTimeField(label=mark_safe('Lock Date:' + _required_star),
            help_text='Time format: HH:MM:SS, 24-hour time',
            widget=CustomSplitDateTimeWidget())
    lock_status = forms.ChoiceField(choices=LOCK_CHOICES,
            label=mark_safe('Lock Status:' + _required_star),
            help_text='status of individual student lock')

    def __init__(self, *args, **kwargs):
        super(SubmissionLockForm, self).__init__(*args, **kwargs)
        self._check_due_date = False
        self._activity_due_date = None

    def check_activity_due_date(self, activity):
        self._check_due_date = True
        self._activity_due_date = activity.due_date

    def clean_lock_status(self):
        lock_status = 'locked'
        if self._check_due_date:    
            if self.cleaned_data['lock_status'] == 'unlock':
                lock_status = 'unlocked'
            elif self.cleaned_data['lock_date'] > datetime.datetime.now():
                lock_status = 'lock pending'
            else:
                lock_status = 'locked'
        return lock_status

    def clean_lock_date(self):
        lock_date = self.cleaned_data['lock_date']
        if self._check_due_date:
            self_lock_date = lock_date
            if self._activity_due_date == None:
                raise forms.ValidationError(u'Please have a valid due date for this activity first')
            elif lock_date < self._activity_due_date:
                raise forms.ValidationError(u'Please select a submission lock date this is after the due date')
        else:
            lock_date = datetime.datetime.now()
        return lock_date