from django import forms
from django.db import models
import datetime
from coredata.models import Unit, Person, Role
from django.utils.safestring import mark_safe
from grades.forms import CustomSplitDateTimeWidget

from peerreview.models import PeerReviewComponent

class AddPeerReviewComponentForm(forms.Form):
    #def __init__(self, *args, **kwargs):
        #super(AddPeerReviewComponentForm, self).__init__(*args, **kwargs)
    due_date = forms.SplitDateTimeField(initial=datetime.datetime.now(), label=mark_safe('Deadline'), required=True,
        help_text='Time format: HH:MM:SS, 24-hour time', widget=CustomSplitDateTimeWidget())
    number_of_reviews = forms.IntegerField(initial=1, required=True,
        help_text= 'This is the number of peer reviews each student is expected to perform')
    
    def clean(self):
        due_date = self.cleaned_data.get('due_date')
        number_of_reviews = self.cleaned_data.get('number_of_reviews')
        if (due_date < datetime.datetime.today()):
            self._errors["due_date"] = self.error_class(["Selected due datetime is before current date"])
        if (number_of_reviews < 1):
            self._errors["number_of_reviews"] = self.error_class(["Number of reviews has to be a whole number greater than 0"])
        #if (number_reviews > class_size):
            #raise forms.ValidationError(u'Peer review number reviews cannot exceed class size!')
        context = { 'due_date' : due_date, 'number_of_reviews' : number_of_reviews}
        return context
    