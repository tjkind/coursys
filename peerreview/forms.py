from django import forms
from django.db import models
import datetime
from coredata.models import Unit, Person, Role

from peerreview.models import PeerReviewComponent

class AddPeerReviewComponentForm(forms.Form):
    #def __init__(self, *args, **kwargs):
    due_date = forms.DateField(initial=datetime.date.today())
    due_time = forms.TimeField(initial=datetime.time(0, 0, 0, 0))
    number_reviews = forms.IntegerField()
    
    def clean(self):
        due_date = self.cleaned_data.get('due_date')
        number_reviews = self.cleaned_data.get('number_reviews')
        if (due_date < datetime.date.today):
            raise forms.ValidationError(u'Selected due date is before current datetime!')
        if (number_reviews < 1):
            raise forms.ValidationError(u'Peer review must have at least 1 number reviews!')
        #elif cleaned_data['number_reviews'] > class_size:
            #raise forms.ValidationError(u'Peer review number reviews cannot exceed class size!')
        context = { 'due_date' : due_date, 'number_reviews' : number_reviews }
        return context
    