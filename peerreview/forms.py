from django import forms
from django.db import models
import datetime
from coredata.models import Unit, Person, Role
from django.utils.safestring import mark_safe
from grades.forms import CustomSplitDateTimeWidget
from django.forms.models import BaseModelFormSet
from django.forms import ModelForm

from peerreview.models import *

class PeerReviewSplitDateTimeWidget(forms.SplitDateTimeWidget):
    """
    Create a custom SplitDateTimeWidget with custom html output format
    """
    def __init__(self, attrs=None, date_format=None, time_format=None):
        super(PeerReviewSplitDateTimeWidget, self).__init__(attrs, date_format, time_format)
        
    def format_output(self, rendered_widgets):
        return mark_safe(u'<div class="datetime">%s %s</div><div class="datetime" style="margin-left: 9.37em">%s %s</div>' % \
            (('Date:'), rendered_widgets[0], ('Time:'), rendered_widgets[1]))

class AddPeerReviewComponentForm(forms.Form):
    def __init__(self, class_size, *args, **kwargs):
        super(AddPeerReviewComponentForm, self).__init__(*args, **kwargs)
        self.class_size = class_size
    due_date = forms.SplitDateTimeField(label=mark_safe('Deadline'), required=True,
        help_text='Time format: HH:MM:SS, 24-hour time', widget=PeerReviewSplitDateTimeWidget())
    number_of_reviews = forms.IntegerField(required=True,
        help_text= 'This is the number of peer reviews each student is expected to perform')
    
    def clean(self):
        class_size = self.class_size
        due_date = self.cleaned_data.get('due_date')
        number_of_reviews = self.cleaned_data.get('number_of_reviews')
        
        if due_date and number_of_reviews:   
            if (due_date < datetime.datetime.today()):
                self._errors["due_date"] = self.error_class(["Selected due datetime is before current date"])
            if (number_of_reviews < 1 or number_of_reviews > class_size):
                self._errors["number_of_reviews"] = self.error_class(["Number of reviews has to be a number between 1 and class size: %i" % class_size])
            context = { 'due_date' : due_date, 'number_of_reviews' : number_of_reviews}
            return context

class StudentReviewForm(forms.Form):
    feedback = forms.CharField(required=False, label='', help_text='Type your review here', widget=forms.Textarea)    

class MarkingSectionForm(ModelForm):
    class Meta:
        model = MarkingSection
        fields = ['title', 'description', 'max_mark']

class BaseMarkingSectionFormSet(BaseModelFormSet): 
    def clean(self):
        """Checks the following:
        1. no two component have the same title  
        2. max mark of each component is non-negative 
        """
        if any(self.errors):
            # Don't bother validating the formset unless each form is valid on its own
             return
        # check titles
        titles = []
        for form in self.forms:
            try: # since title is required, empty title triggers KeyError and don't consider this row
                form.cleaned_data['title']
            except KeyError:      
                continue
            else:  
                title = form.cleaned_data['title']
                if (not form.cleaned_data['deleted']) and title in titles:
                    raise forms.ValidationError(u"Each component must have a unique title")
                titles.append(title)  
        
        # check max marks
        for form in self.forms:
            try:
                form.cleaned_data['title']
            except KeyError:
                continue                        
            max_mark = form.cleaned_data['max_mark']
            if max_mark < 0:
                raise forms.ValidationError(u"Max mark of a component cannot be negative")        