from django import forms
from techreq.models import TechResource, TechRequirement

class TechReqForm(forms.Form):
    name = forms.CharField(required=True, label="Name", max_length=60, 
        help_text="Name of the tech requirement for this course offering.",
        widget=forms.TextInput(attrs={'size':'20'}))
    version = forms.CharField(required=False, label="Version", max_length=30, 
        help_text="A optional version of the tech requirement.",
        widget=forms.TextInput(attrs={'size':'20'}))
    quantity = forms.IntegerField(required=False, label="Quantity",
        help_text="A optional quantity of the tech requirement.")
    location = forms.CharField(required=False, label="Location", max_length=20, 
        help_text="The location where the tech requirement is required.",
        widget= forms.TextInput(attrs={'size':'20'}))
    notes = forms.CharField(required=False, label="Notes",
        help_text="Any additional notes about the tech requirement.",
        widget= forms.Textarea())

    def __init__(self, course_offering, *args, **kwargs):
        super(TechReqForm, self).__init__(*args, **kwargs)
        self.course_offering = course_offering


class TechResource(forms.Form):
	name = forms.CharField(required=True, label="Resource Name", max_length= 50)
	#unit=  ----not sure about it yet:   Foreign Key
	version = forms.CharField(required=False, label="Version", max_length=50) 
	quantity = forms.IntegerField(required=False, label="Quantity"")
   	location =  forms.CharField(required=False, label="Location", max_length=50)
	notes = forms.CharField(required=False, label="Notes", widget= forms.Textarea())

