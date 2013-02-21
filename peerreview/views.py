from django.core.urlresolvers import reverse, resolve
from django.core.mail.message import EmailMessage
from django.template import RequestContext, Context, loader
from django.shortcuts import render_to_response, get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from datetime import date, datetime
from urlparse import urlparse
from courselib.auth import requires_role, HttpResponseRedirect, \
    ForbiddenResponse, requires_course_staff_by_slug, is_course_student_by_slug

from grades.models import Activity
from coredata.models import Course, CourseOffering
from peerreview.forms import AddPeerReviewComponentForm, StudentLockForm
from peerreview.models import *
from submissionlock.models import is_student_locked, SubmissionLock

@requires_course_staff_by_slug
def add_peer_review_component(request, course_slug, activity_slug):
    course = get_object_or_404(CourseOffering, slug = course_slug)
    activity = get_object_or_404(Activity, slug = activity_slug)
    class_size = activity.offering.members.count()
    if request.method == 'POST':
        form = AddPeerReviewComponentForm(class_size, request.POST)
        if form.is_valid():
            try: #see if peerreview component already exists for this activity
                peerreview_component = PeerReviewComponent.objects.get(activity=activity)
                peerreview_component.due_date = form.cleaned_data['due_date']
                peerreview_component.number_of_reviews = form.cleaned_data['number_of_reviews']
                peerreview_component.save()
            except: #else create a peerreview component
                peerreview_component = PeerReviewComponent.objects.create(
                    activity = activity,
                    due_date = form.cleaned_data['due_date'],
                    number_of_reviews = form.cleaned_data['number_of_reviews'],
                )
            return HttpResponseRedirect(reverse('grades.views.activity_info', kwargs={'course_slug': course_slug, 'activity_slug': activity_slug}))
    else:
        form = AddPeerReviewComponentForm(class_size)

    context = {
        'form' : form,
        'course' : course,
        'activity' : activity,
    }
    return render(request, "peerreview/add_peer_review_component.html", context)

@login_required
def student_view(request, course_slug, activity_slug):
    student_member = get_object_or_404(Member, person__userid=request.user.username, offering__slug=course_slug)
    activity = Activity.objects.get(slug=activity_slug)
    locked = is_student_locked(activity=activity, student=student_member)

    if locked:
        return _student_peer_review(request=request, course_slug=course_slug, student_member=student_member, activity=activity)
    elif not locked:
        return _request_student_lock(request=request, course_slug=course_slug, student_member=student_member, activity=activity)
    else:
        return ForbiddenResponse(request)

def _request_student_lock(request, course_slug, student_member, activity):
    course = get_object_or_404(CourseOffering, slug = course_slug)
    if request.method == 'POST':
        if 'cancel' not in request.POST:
            try:
                student_lock = SubmissionLock.objects.get(activity=activity, member=student_member)
                student_lock.status = 'locked'
                student_lock.effective_date = datetime.datetime.now()
                student_lock.save()
            except:
                submission_lock = SubmissionLock.objects.create(
                    member=student_member,
                    activity=activity,
                    status='locked',
                )
            return HttpResponseRedirect(reverse('peerreview.views.student_view', kwargs={'course_slug': course_slug, 'activity_slug': activity.slug}))
        else:
            return HttpResponseRedirect(reverse('grades.views.course_info', kwargs={'course_slug': course_slug}))
    else:
        form = StudentLockForm()
    
    context = {
        'form':form,
        'course':course,
        'activity':activity,
    }
    return render(request, "peerreview/request_student_lock.html", context)

def _student_peer_review(request, course_slug, student_member, activity):
    course = get_object_or_404(CourseOffering, slug = course_slug)
    messages.warning(request, "You are Locked")
    context = {
        'course':course,
        'activity':activity,
    }
    return render(request, "peerreview/student_peer_review.html", context)