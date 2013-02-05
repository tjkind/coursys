from submissionlock.models import SubmissionLock, ActivityLock
from grades.models import Activity
from coredata.models import CourseOffering, Member
from courselib.auth import requires_course_staff_by_slug

from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse

from submissionlock.forms import *
import datetime

def _effective_lock_date(activity_lock, activity, student):
    try:
        student_lock = SubmissionLock.objects.get(activity=activity, member=student)
        return student_lock.effective_date
    except:
        if activity_lock == None:
            return None
        else:
            return activity_lock.effective_date

    return None

def _submission_lock_status(activity_lock, activity, student):
    try:
        student_lock = SubmissionLock.objects.get(activity=activity, member=student)
        return student_lock.status
    except:
        if activity_lock == None:
            return "unlocked"
        elif activity_lock.effective_date > datetime.datetime.now():
            return "lock pending"
        else:
            return "locked"

    return "unlocked"

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