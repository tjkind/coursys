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
from coredata.models import Course, CourseOffering, Member
from peerreview.forms import AddPeerReviewComponentForm
from peerreview.models import *
from submissionlock.models import is_student_locked, SubmissionLock, ActivityLock
from submission.models import get_current_submission

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
                print "Exists and edited"
            except: #else create a peerreview component
                peerreview_component = PeerReviewComponent.objects.create(
                    activity = activity,
                    due_date = form.cleaned_data['due_date'],
                    number_of_reviews = form.cleaned_data['number_of_reviews'],
                )
                print "Created"
            return HttpResponseRedirect(reverse('grades.views.activity_info', kwargs={'course_slug': course_slug, 'activity_slug': activity_slug}))
    else:
        form = AddPeerReviewComponentForm(class_size)

    context = {
        'form' : form,
        'course' : course,
        'activity' : activity,
    }
    return render(request, "peerreview/add_peer_review_component.html", context)

@requires_course_staff_by_slug
def edit_peer_review_component(request, course_slug, activity_slug):
    course = get_object_or_404(CourseOffering, slug = course_slug)
    activity = get_object_or_404(Activity, slug = activity_slug)
    class_size = activity.offering.members.count()
    peerreview_component = get_object_or_404(PeerReviewComponent, activity=activity)
    if request.method == 'POST':
        form = AddPeerReviewComponentForm(class_size, request.POST)
        if form.is_valid():
            peerreview_component.due_date = form.cleaned_data['due_date']
            peerreview_component.number_of_reviews = form.cleaned_data['number_of_reviews']
            peerreview_component.save()
        return HttpResponseRedirect(reverse('grades.views.activity_info', kwargs={'course_slug': course_slug, 'activity_slug': activity_slug}))
    else:
        form = AddPeerReviewComponentForm(class_size, initial=
        {
            'due_date':peerreview_component.due_date,
            'number_of_reviews':peerreview_component.number_of_reviews,
        })

    context = {
        'form' : form,
        'course' : course,
        'activity' : activity,
    }
    return render(request, "peerreview/edit_peer_review_component.html", context)
    
@requires_course_staff_by_slug
def peer_review_info_staff(request, course_slug, activity_slug):
    course = get_object_or_404(CourseOffering, slug=course_slug)
    activity = get_object_or_404(Activity, slug=activity_slug)
    
    try:
        peerreview = get_object_or_404(PeerReviewComponent, activity=activity)
        print "Found"
    except:
        peerreview = None
        print "Not Found"

    # build list of all students and grades
    students = Member.objects.filter(role="STUD", offering=activity.offering).select_related('person')

    context = {'course': course, 'activity': activity, 'students': students, 'peerreview':peerreview}
    return render(request, 'peerreview/peer_review_info_staff.html', context)

@login_required
def peer_review_info_student(request, course_slug, activity_slug):
    student_member = get_object_or_404(Member, person__userid=request.user.username, offering__slug=course_slug)
    course = get_object_or_404(CourseOffering, slug = course_slug)
    activity = get_object_or_404(Activity, slug=activity_slug, offering=course)
    peerreview = get_object_or_404(PeerReviewComponent, activity=activity)
    
    locked = is_student_locked(activity=activity, student=student_member)

    if locked:
        return _student_peer_review(request=request, course=course, student_member=student_member, peerreview=peerreview)
    elif not locked:
        return _request_student_lock(request=request, course=course, student_member=student_member, activity=activity)
    else:
        return ForbiddenResponse(request)

def _request_student_lock(request, course, student_member, activity):
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
            return HttpResponseRedirect(reverse('peerreview.views.peer_review_info_student', kwargs={'course_slug': course.slug, 'activity_slug': activity.slug}))
        else:
            return HttpResponseRedirect(reverse('grades.views.course_info', kwargs={'course_slug': course.slug}))
    
    context = {
        'course':course,
        'activity':activity,
    }
    return render(request, "peerreview/request_student_lock.html", context)

def _student_peer_review(request, course, student_member, peerreview):
    activity = peerreview.activity
    student_member_list = Member.objects.filter(offering=course, role="STUD").exclude(pk=student_member.pk)
    try:
        activity_lock = ActivityLock.objects.get(activity=activity)
    except:
        activity_lock = False

    review_components = list(StudentPeerReview.objects.filter(reviewer=student_member))
    if len(review_components) < peerreview.number_of_reviews:
        if activity_lock and activity_lock.display_lock_status()=="Locked":
            submitted_students = []
            for student in student_member_list:
                sub, sub_component = get_current_submission(student.person, activity)
                if sub:
                    submitted_students.append(student)
            review_components = generate_peerreview(peerreview=peerreview, students=submitted_students, student_member=student_member, overlimit=True)
        else:
            locked_students = Member.objects.filter(offering=course, role="STUD", pk__in=SubmissionLock.objects.filter(member__in=(student_member_list)).values('member'))
            review_components = generate_peerreview(peerreview=peerreview, students=locked_students, student_member=student_member)
    
    context = {
        'review_components':review_components,
        'course':course,
        'activity':activity,
    }
    return render(request, "peerreview/student_peer_review.html", context)

def student_review(request, course_slug, activity_slug, peerreview_slug):
    peerreview = StudentPeerReview.objects.get(slug=peerreview_slug)
    messages.warning(request,peerreview.reviewee)
    return ForbiddenResponse(request)