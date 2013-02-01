from django import forms
from django.db import models
from coredata.models import Unit, Person, Role
from grades.models import Activity

from peerreview.models import PeerReviewComponent

class AddPeerReviewComponentForm(forms.ModelForm):
    def __init__(self, units, *args, **kwargs):
        #activity = Activity.objects.filter(offering__in=Request.POST)
        #activity = Activity.objects.all()
        pass
    
    class Meta:
        model = PeerReviewComponent
        exclude = {'config', 'deleted'}
