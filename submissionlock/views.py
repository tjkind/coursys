from submissionlock.models import SubmissionLock, ActivityLock
from grades.models import Activity
from coredata.models import CourseOffering, Member, Person
from courselib.auth import requires_course_staff_by_slug, HttpResponseRedirect

from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse

from submissionlock.forms import *
import datetime

def _effective_lock_date(activity_lock, activity, student):
    try:
        submission_lock = SubmissionLock.objects.get(activity=activity, member=student)
        return submission_lock.effective_date
    except:
        if activity_lock == None:
            return None
        else:
            return activity_lock.effective_date

def _submission_lock_status(activity_lock, activity, student):
    try:
        submission_lock = SubmissionLock.objects.get(activity=activity, member=student)
        return submission_lock.status
    except:
        if activity_lock == None:
            return "unlocked"
        elif activity_lock.effective_date > datetime.datetime.now():
            return "lock pending"
        else:
            return "locked"

def _activity_lock_status(activity_lock):
    if activity_lock == None:
        return "unlocked"
    elif activity_lock.effective_date > datetime.datetime.now():
        return "lock pending"
    else:
        return "locked"

    return "unlocked"

@requires_course_staff_by_slug
def submission_lock(request, course_slug, activity_slug):
    activity = Activity.objects.get(slug=activity_slug)
    course = get_object_or_404(CourseOffering, slug=course_slug)
    student_member_list = Member.objects.filter(offering=course, role="STUD")
    students = []
    try:
        activity_lock = ActivityLock.objects.get(activity=activity)
    except:
        activity_lock = None

    for student_member in student_member_list:
        students.append({
            'name' : student_member.person.name,
            'emplid' : student_member.person.emplid,
            'userid' : student_member.person.userid,
            'lock_date' : _effective_lock_date(activity_lock=activity_lock, activity=activity, student=student_member),
            'lock_status' : _submission_lock_status(activity_lock=activity_lock, activity=activity, student=student_member),
        })

    context = {
        'activity_lock_status' : _activity_lock_status(activity_lock=activity_lock),
        'activity_lock' : activity_lock,
        'students' : students,
        'course' : course,
        'activity' : activity,
    }  
    
    return render(request, 'submissionlock/submission_lock.html', context)

@requires_course_staff_by_slug
def staff_edit_submission_lock(request, course_slug, activity_slug, userid):
    activity = Activity.objects.get(slug=activity_slug)
    course = get_object_or_404(CourseOffering, slug=course_slug)
    student = get_object_or_404(Member, person__userid=userid, offering__slug=course_slug)
    try:
        activity_lock = ActivityLock.objects.get(activity=activity)
    except:
        activity_lock = None

    if request.method == 'POST':
        form = SubmissionLockForm(request.POST)
        form.check_activity_due_date(activity)
        if form.is_valid(): #if all form validation goes through
            lock_date = form.cleaned_data['lock_date']
            lock_status = form.cleaned_data['lock_status']

            try: #see if submission lock already exists for this student
                submission_lock = SubmissionLock.objects.get(activity=activity, member=student)
                submission_lock.status = lock_status
                submission_lock.effective_date = lock_date
                submission_lock.save()
            except:
                submission_lock = SubmissionLock.objects.create(
                    member=student,
                    activity=activity,
                    status=lock_status,
                    effective_date=lock_date,
                )
            return HttpResponseRedirect(reverse('submissionlock.views.submission_lock', kwargs={'course_slug': course_slug, 'activity_slug': activity_slug}))

    else:
        #find initial values for form
        student_lock_status = _submission_lock_status(activity_lock=activity_lock, activity=activity, student=student)
        student_lock_effective_date = _effective_lock_date(activity_lock=activity_lock, activity=activity, student=student)
        
        #use verbs instead of status to clearify for users; lock/unlock instead of locked/unlocked/lock_pending
        if student_lock_status == "unlocked":
            lock_status = 'unlock'
        else:
            lock_status = 'lock'

        #if None is returned from _effective_lock_date use current time
        if student_lock_effective_date == None:
            lock_date = datetime.datetime.now()
        else:
            lock_date = student_lock_effective_date

        form_initials = {
            'lock_status' : lock_status,
            'lock_date' : lock_date,
        }
        form = SubmissionLockForm(initial=form_initials)

    context = {
        'form' : form,
        'course' : course,
        'activity' : activity,
        'userid' : userid,
    }

    return render(request, 'submissionlock/staff_edit_submission_lock.html', context)
