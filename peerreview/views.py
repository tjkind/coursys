from django.core.urlresolvers import reverse, resolve
from django.core.mail.message import EmailMessage
from django.template import RequestContext, Context, loader
from django.shortcuts import render_to_response, get_object_or_404, render
from datetime import date
from urlparse import urlparse
from courselib.auth import requires_role, HttpResponseRedirect, \
    ForbiddenResponse, requires_course_staff_by_slug
from grades.models import Activity
from peerreview.forms import AddPeerReviewComponentForm


@requires_course_staff_by_slug
def add_peer_review_component(request, course_slug, activity_slug):
    activity = get_object_or_404(Activity, slug = activity_slug)
    if request.method == 'POST':
        form = AddPeerReviewComponentForm(request.POST)
        if form.is_valid():
            #Peer_Review_Component = form.save()
            #do something
            return HttpResponseRedirect(reverse('grades.views.activity_info', kwargs={'course_slug': course_slug, 'activity_slug': activity_slug}))
    else:
        form = AddPeerReviewComponentForm()

    context = {
        'form' : form,
        'course_slug' : course_slug,
        'activity_slug' : activity_slug,
    }
    return render(request, "peerreview/add_peer_review_component.html", context)
