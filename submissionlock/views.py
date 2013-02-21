from submissionlock.models import SubmissionLock, ActivityLock
from grades.models import Activity
from coredata.models import CourseOffering, Member, Person
from courselib.auth import requires_course_staff_by_slug, HttpResponseRedirect

from django.contrib import messages
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse

from submissionlock.forms import *
import datetime

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
        lock_date = None
        lock_status = "Unlocked"
        try:
            student_lock = SubmissionLock.objects.get(activity=activity,member=student_member)
            lock_date = student_lock.display_lock_date()
            lock_status = student_lock.display_lock_status()
        except:
            if activity_lock:
                lock_date = activity_lock.display_lock_date()
                lock_status = activity_lock.display_lock_status()

        students.append({
            'name' : student_member.person.name,
            'emplid' : student_member.person.emplid,
            'userid' : student_member.person.userid,
            'lock_date' : lock_date,
            'lock_status' : lock_status,
        })

    activity_lock_status = "Unlocked"
    if activity_lock:
        activity_lock_status = activity_lock.display_lock_status()
    context = {
        'activity_lock_status' : activity_lock_status,
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
        form = StaffLockForm(request.POST)
        form.check_activity_due_date(activity)
        if form.is_valid(): #if all form validation goes through
            try: #see if submission lock already exists for this student
                submission_lock = SubmissionLock.objects.get(activity=activity, member=student)
                submission_lock.status = form.cleaned_data['lock_status']
                submission_lock.effective_date = form.cleaned_data['lock_date']
                submission_lock.save()
            except:
                submission_lock = SubmissionLock.objects.create(
                    member=student,
                    activity=activity,
                    status=form.cleaned_data['lock_status'],
                    effective_date=form.cleaned_data['lock_date'],
                )
            return HttpResponseRedirect(reverse('submissionlock.views.submission_lock', kwargs={'course_slug': course_slug, 'activity_slug': activity_slug}))
    else:
        if activity.due_date:
            lock_date = activity.due_date
        else:
            lock_date = datetime.datetime.now()
        form_initials = {
            'lock_status' : 'locked',
            'lock_date' : lock_date,
        }
        form = StaffLockForm(initial=form_initials)

    context = {
        'form' : form,
        'course' : course,
        'activity' : activity,
        'userid' : userid,
    }

    return render(request, 'submissionlock/staff_edit_submission_lock.html', context)

def _clean_submission_locks(activity):
    submission_locks = SubmissionLock.objects.filter(activity=activity)
    submission_locks.delete()


@requires_course_staff_by_slug
def staff_edit_activity_lock(request, course_slug, activity_slug):
    activity = Activity.objects.get(slug=activity_slug)
    course = get_object_or_404(CourseOffering, slug=course_slug)
    try:
        activity_lock = ActivityLock.objects.get(activity=activity)
    except:
        activity_lock = None

    if request.method == 'POST':
        form = StaffLockForm(request.POST)
        form.check_activity_due_date(activity)
        if form.is_valid(): #if all form validation goes through
            if form.cleaned_data['lock_status'] == 'unlocked' and activity_lock:
                activity_lock.delete()
            elif form.cleaned_data['lock_status'] == 'lock_pending':
                if activity_lock:
                    activity_lock.effective_date = form.cleaned_data['lock_date']
                    activity_lock.save()
                else:
                    activity_lock = ActivityLock.objects.create(
                        activity=activity,
                        effective_date=form.cleaned_data['lock_date'],
                    )
            _clean_submission_locks(activity=activity)

            return HttpResponseRedirect(reverse('submissionlock.views.submission_lock', kwargs={'course_slug': course_slug, 'activity_slug': activity_slug}))
    else:
        if activity_lock:
            activity_lock_status = _activity_lock_status(activity_lock=activity_lock, activity=activity)
            if activity_lock_status == "Lock Pending":
                if activity_lock.effective_date > datetime.datetime.now():
                    lock_status = 'lock_pending'
                else:
                    lock_status = 'locked'
            elif activity_lock_status == "Locked":
                lock_status = 'locked'
            else:
                lock_status = 'unlocked'
            lock_date = activity_lock.effective_date
        else:
            lock_status = 'locked'
            if activity.due_date:
                lock_date = activity.due_date
            else:
                lock_date = datetime.datetime.now()

        form_initials = {
            'lock_status' : lock_status,
            'lock_date' : lock_date,
        }
        form = StaffLockForm(initial=form_initials)

    locked_students = SubmissionLock.objects.filter(activity=activity)
    if locked_students:
        students = []
        for student in locked_students:
            students.append(student.member.person.name())
        messages.warning(request, "You are about to edit the activity lock, which will clear the locks against " + ", ".join(students) + ".")

    context = {
        'form' : form,
        'course' : course,
        'activity' : activity,
    }
    
    return render(request, 'submissionlock/staff_edit_activity_lock.html', context)