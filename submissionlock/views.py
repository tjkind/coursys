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
        if submission_lock.status == 'unlocked':
            return None
        if submission_lock.status == 'lock_pending':
            if activity.due_date == None:
                return None
            elif submission_lock.effective_date < activity.due_date:
                return None
        return submission_lock.effective_date
    except:
        if activity.due_date == None or activity_lock == None:
            return None
        elif activity_lock.effective_date < activity.due_date:
            return None
        elif activity.due_date == None:
            return None
        else:
            return activity_lock.effective_date

def _submission_lock_status(activity_lock, activity, student):
    try:
        submission_lock = SubmissionLock.objects.get(activity=activity, member=student)
        if submission_lock.status == 'locked':
            return "Locked"
        elif submission_lock.status == 'lock_pending':            
            if activity.due_date == None:
                return "Unlocked"
            elif submission_lock.effective_date < activity.due_date:
                return "Unlocked"
            elif submission_lock.effective_date < datetime.datetime.now():
                return "Locked"
            else:
                return "Lock Pending"
        else:
            return "Unlocked"
    except:
        if activity.due_date == None or activity_lock == None:
            return "Unlocked"
        elif activity.due_date == None:
            return "Unlocked"
        elif activity_lock.effective_date < activity.due_date:
            return "Unlocked"
        elif activity_lock.effective_date > datetime.datetime.now():
            return "Lock Pending"
        else:
            return "Locked"

def _activity_lock_status(activity_lock, activity):
    if activity.due_date == None or activity_lock == None:
        return "Unlocked"
    elif activity_lock.effective_date < activity.due_date:
        return "Unlocked"
    elif activity_lock.effective_date > datetime.datetime.now():
        return "Lock Pending"
    else:
        return "Locked"

def _is_student_locked(activity, student):
    locked = False
    try: #first check ActivityLock
        activity_lock = ActivityLock.objects.get(activity=activity)
    except:
        activity_lock = None

    #check ActivityLock and activity.due_date
    if activity_lock == None or activity.due_date == None:
        locked = False
    elif activity_lock.effective_date < activity.due_date:
        locked = False
    elif activity_lock.effective_date < datetime.datetime.now():
        locked = True

    try: #SubmissionLock has hierachy and will overshadow previous checks
        submission_lock = SubmissionLock.objects.get(activity=activity, member=student)
        if submission_lock.status == 'locked': #this will automatically return true because it's only set when student try to perform peer review and agreed to lock submissions
            return True
        elif submission_lock.status == 'lock_pending' and activity.due_date != None: #status "lock_pending" can only be set by the staff and therefore must taken into account the activity due date
            if submission_lock.effective_date < activity.due_date:
                locked = False
            elif submission_lock.effective_date < datetime.datetime.now():
                locked = True
            else:
                locked = False
        elif submission_lock.status == 'unlocked':
            locked = False
    except:
        pass
    return locked

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
        'activity_lock_status' : _activity_lock_status(activity_lock=activity_lock, activity=activity),
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
        student_lock_status = _submission_lock_status(activity_lock=activity_lock, activity=activity, student=student)
        student_lock_effective_date = _effective_lock_date(activity_lock=activity_lock, activity=activity, student=student)
        
        #setting initial lock status values
        if student_lock_status == "Lock Pending":
            if student_lock_effective_date > datetime.datetime.now():
                lock_status = 'lock_pending'
            else:
                lock_status = 'locked'
        elif student_lock_status == "Locked":
            lock_status = 'locked'
        else:
            lock_status = 'unlocked'

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
