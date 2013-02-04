from submissionlock.models import SubmissionLock
from grades.models import Activity
from coredata.models import CourseOffering, Member

from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse

from submissionlock.forms import *
from django.forms.models import modelformset_factory
LockFormSet = modelformset_factory(SubmissionLock)

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
        #form = SubmissionLockForm(request.POST)
        formset = LockFormSet(request.POST)
        if form.isvalid():
            #...
            return HttpResponseRedirect(reverse('submissionlock.views.submission_lock'))
    else:
        #form = SubmissionLockForm()
        formset = LockFormSet()
    
    course_activity_slug = course_slug + '/\+' + activity_slug
    context = {
        'students': students,
        'course_slug': course_slug,
        'activity_slug': activity_slug,
        'locked_students': locked_students,
        'course_slug' : course_slug,
        'activity_slug' : activity_slug,
        'course_activity_slug' : course_activity_slug,
        #'form' : form,
        'formset' : formset,
    }  
    
    return render(request, 'submissionlock/test.html', context)

def _apply_lock(course, activity, lock_date):
    students = Member.objects.filter(offering=course, role="STUD").select_related('person', 'offering')
    for student in students:
        SubmissionLock.objects.create(member=student,
                                    activity=activity,
                                    effective_date=lock_date)