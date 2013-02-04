from submissionlock.models import SubmissionLock
from grades.models import Activity
from coredata.models import CourseOffering, Member
from courselib.auth import requires_course_staff_by_slug

from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse

from submissionlock.forms import *

@requires_course_staff_by_slug
def submission_lock(request, course_slug, activity_slug):
    activity = Activity.objects.get(slug=activity_slug)
    course = get_object_or_404(CourseOffering, slug=course_slug)
    students = Member.objects.filter(offering=course, role="STUD")

    if request.method == 'POST':
        form = SubmissionLockForm(request.POST, students, activity)
        if form.isvalid():
            a = form.clean(self)
            #To Be Done ...
            return HttpResponseRedirect(reverse('submissionlock.views.submission_lock'))
    else:
        form = SubmissionLockForm(students, activity)
    
    context = {
        'course' : course,
        'activity' : activity,
        'form' : form,
    }  
    
    return render(request, 'submissionlock/submission_lock.html', context)

def _apply_lock(course, activity, lock_date):
    students = Member.objects.filter(offering=course, role="STUD").select_related('person', 'offering')
    for student in students:
        SubmissionLock.objects.create(member=student,
                                    activity=activity,
                                    effective_date=lock_date)