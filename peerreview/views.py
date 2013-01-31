from django.core.urlresolvers import reverse, resolve
from django.core.mail.message import EmailMessage
from django.template import RequestContext, Context, loader
from django.shortcuts import render_to_response, get_object_or_404, render
from datetime import date
from urlparse import urlparse
from courselib.auth import requires_role, HttpResponseRedirect, \
    ForbiddenResponse
from peerreview.forms import AddPeerReviewComponentForm

def add_peer_review_component(request, course_slug):
    if request.method == 'POST':
        form = AddPeerReviewComponentForm(request.units, request.POST)
        if form.is_valid():
            Peer_Review_Component = form.save()
            return HttpResponseRedirect(reverse('grades.views.activity_choice'))
    else:
        form = AddPeerReviewComponentForm(request.units)
    
    return render(request, "peerreview/add_peer_review_component.html", {'form':form,})