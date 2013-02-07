from django import forms
from django.conf import settings
from django.forms.fields import CharField, ChoiceField
from django.utils.safestring import mark_safe
import datetime

from grades.models import Activity
from grades.forms import CustomSplitDateTimeWidget
from coredata.models import Member
from submissionlock.models import SubmissionLock, ActivityLock, LOCK_STATUS_CHOICES

class LockForm(forms.Form):
    lock_status = forms.ChoiceField(choices=LOCK_STATUS_CHOICES,
            label=mark_safe('Lock Status:'),
            help_text='status of individual student lock',
            widget=forms.RadioSelect())
    lock_date = forms.SplitDateTimeField(label=mark_safe('Lock Date:'), required=False,
            help_text='Time format: HH:MM:SS, 24-hour time',
            widget=CustomSplitDateTimeWidget())

    def __init__(self, *args, **kwargs):
        super(LockForm, self).__init__(*args, **kwargs)
        self._check_due_date = False
        self._activity_due_date = None

    def check_activity_due_date(self, activity):
        self._check_due_date = True
        self._activity_due_date = activity.due_date

class StaffLockForm(LockForm):
    def clean(self):
        cleaned_data = super(StaffLockForm, self).clean()
        if self._check_due_date:
            if cleaned_data['lock_status'] == 'lock_pending':
                if self._activity_due_date == None:
                    pass
                elif cleaned_data['lock_date'] == None:
                    raise forms.ValidationError(u'Please have a valid lock pending date.')
                elif cleaned_data['lock_date'] < self._activity_due_date:
                    raise forms.ValidationError(u'Please select a submission lock date that is after the due date.')

            if cleaned_data['lock_status'] == 'locked':
                cleaned_data['lock_date'] = datetime.datetime.now()
                if self._activity_due_date == None:
                    pass
                elif cleaned_data['lock_date'] < self._activity_due_date:
                    raise forms.ValidationError(u'May not lock student submission until past the due date.')

            if cleaned_data['lock_status'] == 'locked': #this is to ensure all staff "lock" to SubmissionLock are stored as lock_pending
                cleaned_data['lock_status'] = 'lock_pending'
            
            if cleaned_data['lock_status'] == 'lock_pending' and self._activity_due_date == None:
                raise forms.ValidationError(u'You may only use "Unlock" option until there is a valid due date for this activity.')
        return cleaned_data
