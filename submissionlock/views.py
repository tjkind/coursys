from submissionlock.models import SubmissionLock
from grades.models import Activity
from coredata.models import CourseOffering, Member

from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse

from submissionlock.forms import *

#def submission_lock(request, course_slug, activity_slug):
#    activity = Activity.objects.get(slug=activity_slug)
#    course = get_object_or_404(CourseOffering, slug=course_slug)
#    students = Member.objects.filter(offering=course, role="STUD").select_related('person', 'offering')
#    locked_students = SubmissionLock.objects.filter(activity=activity).select_related('member', 'effective_date')
#    context = {
#        'students': students,
#        'course_slug': course_slug,
#        'activity_slug': activity_slug,
#        'locked_students': locked_students,
#    }
#    return render(request, 'submissionlock/submission_lock.html', context)

def submission_lock(request, course_slug, activity_slug):
    activity = Activity.objects.get(slug=activity_slug)
    course = get_object_or_404(CourseOffering, slug=course_slug)
    students = Member.objects.filter(offering=course, role="STUD").select_related('person', 'offering')
    locked_students = SubmissionLock.objects.filter(activity=activity).select_related('member', 'effective_date')

    if request.method == 'POST':
        form = SubmissionLockForm(request.POST, students, locked_students)
        if form.isvalid():
            a = form.clean(self)
            #To Be Done ...
            return HttpResponseRedirect(reverse('submissionlock.views.submission_lock'))
    else:
        form = SubmissionLockForm(students, locked_students)
    
    context = {
        'students': students,
        'course_slug': course_slug,
        'activity_slug': activity_slug,
        'locked_students': locked_students,
        'course_slug' : course_slug,
        'activity_slug' : activity_slug,
        'form' : form,
    }  
    
    return render(request, 'submissionlock/submission_lock.html', context)

def _apply_lock(course, activity, lock_date):
    students = Member.objects.filter(offering=course, role="STUD").select_related('person', 'offering')
    for student in students:
        SubmissionLock.objects.create(member=student,
                                    activity=activity,
                                    effective_date=lock_date)