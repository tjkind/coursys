from django import forms
from django.db import models
import datetime
from coredata.models import Unit, Person, Role
from django.utils.safestring import mark_safe
from grades.forms import CustomSplitDateTimeWidget

from peerreview.models import PeerReviewComponent

class AddPeerReviewComponentForm(forms.Form):
    #def __init__(self, class_size, *args, **kwargs):
    #due_date = forms.DateField(initial=datetime.date.today())
    #due_time = forms.TimeField(initial=datetime.time(0, 0, 0, 0))
    due_date = forms.SplitDateTimeField(initial=datetime.datetime.now(), label=mark_safe('Deadline'), required=True,
            help_text='Time format: HH:MM:SS, 24-hour time', widget=CustomSplitDateTimeWidget())
    number_reviews = forms.IntegerField(initial=1, required=True)
    active = forms.BooleanField(required=False)
    
    def clean(self):
        due_date = self.cleaned_data.get('due_date')
        number_reviews = self.cleaned_data.get('number_reviews')
        active = self.cleaned_data.get('active')
        if (due_date < datetime.datetime.today()):
            raise forms.ValidationError(u'Selected due datetime is before current date!')
        if (number_reviews < 1):
            raise forms.ValidationError(u'Peer review must have at least 1 number reviews!')
        #if (number_reviews > class_size):
            #raise forms.ValidationError(u'Peer review number reviews cannot exceed class size!')
        context = { 'due_date' : due_date, 'number_reviews' : number_reviews, 'active' : active }
        return context
    