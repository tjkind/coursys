from django import forms
from django.db import models
import datetime
from coredata.models import Unit, Person, Role
from django.utils.safestring import mark_safe
from grades.forms import CustomSplitDateTimeWidget

from peerreview.models import PeerReviewComponent

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
    due_date = forms.SplitDateTimeField(initial=datetime.datetime.now(), label=mark_safe('Deadline'), required=True,
        help_text='Time format: HH:MM:SS, 24-hour time', widget=PeerReviewSplitDateTimeWidget())
    number_of_reviews = forms.IntegerField(initial=1, required=True,
        help_text= 'This is the number of peer reviews each student is expected to perform')
    
    
    #raise forms.ValidationError(u'Peer review number reviews cannot exceed class size!')
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



    