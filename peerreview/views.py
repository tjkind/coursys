from django.core.urlresolvers import reverse, resolve
from django.core.mail.message import EmailMessage
from django.template import RequestContext, Context, loader
from django.shortcuts import render_to_response, get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.contrib.sites.models import get_current_site
from django.contrib import messages
from django.forms.models import modelformset_factory

from datetime import date, datetime
from urlparse import urlparse
from courselib.auth import requires_role, HttpResponseRedirect, \
    ForbiddenResponse, requires_course_staff_by_slug, is_course_student_by_slug

from grades.models import Activity
from coredata.models import Course, CourseOffering, Member
from peerreview.forms import *
from peerreview.models import *
from submissionlock.models import is_student_locked, SubmissionLock, ActivityLock
from submission.models import SubmissionComponent, GroupSubmission, StudentSubmission, get_current_submission, select_all_submitted_components, select_all_components


def _save_marking_section(formset, peerreview_component):
    position = 0
    for form in formset.forms:
        try:  # title is required, empty title triggers KeyError and don't consider this row
            form.cleaned_data['title']
        except KeyError:
            continue
        else:
            instance = form.save(commit = False)
            instance.peer_review_component = peerreview_component
            instance.position = position
            instance.save()
            """
            instance = MarkingSection.objects.create(
                peer_review_component = peerreview_component,
                title = form.cleaned_data['title'],
                description = form.cleaned_data['description'],
                max_mark = form.cleaned_data['max_mark'],
                position = position
            )
            """
            position += 1

@requires_course_staff_by_slug
def add_peer_review_component(request, course_slug, activity_slug):
    error_info = None
    course = get_object_or_404(CourseOffering, slug = course_slug)
    activity = get_object_or_404(Activity, slug = activity_slug)
    try:
        activity_lock = ActivityLock.objects.get(activity=activity)
    except:
        activity_lock = None
        messages.error(request, "May not add Peer Review to this activity without an activity lock")
        return HttpResponseRedirect(reverse('grades.views.activity_info', kwargs={'course_slug': course_slug, 'activity_slug': activity_slug}))
        
    fields = ('title', 'description', 'max_mark', 'deleted',)
    MarkingSectionFormSet = modelformset_factory(MarkingSection, fields=fields, \
                                              formset=BaseMarkingSectionFormSet, \
                                              can_delete = False, extra = 10)

    class_size = activity.offering.members.count()
    if request.method == 'POST':
        form = AddPeerReviewComponentForm(class_size, request.POST)
        formset = MarkingSectionFormSet(request.POST)
        if not formset.is_valid(): 
            if formset.non_form_errors(): # not caused by error of an individual form
                error_info = formset.non_form_errors()[0]  
        elif form.is_valid() and formset.is_valid():
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

            _save_marking_section(formset, peerreview_component)
                        
            return HttpResponseRedirect(reverse('grades.views.activity_info', kwargs={'course_slug': course_slug, 'activity_slug': activity_slug}))
    else:
        form = AddPeerReviewComponentForm(class_size)
        formset = MarkingSectionFormSet(queryset=MarkingSection.objects.none())

    if error_info:
        messages.add_message(request, messages.ERROR, error_info)
    context = {
        'form' : form,
        'formset' : formset,
        'course' : course,
        'activity' : activity,
    }
    return render(request, "peerreview/add_peer_review_component.html", context)

@requires_course_staff_by_slug
def edit_peer_review_component(request, course_slug, activity_slug):
    error_info = None
    course = get_object_or_404(CourseOffering, slug = course_slug)
    activity = get_object_or_404(Activity, slug = activity_slug)
    class_size = activity.offering.members.count()
    peerreview_component = get_object_or_404(PeerReviewComponent, activity=activity)
    try:
        activity_lock = ActivityLock.objects.get(activity=activity)
        if activity_lock.display_lock_status() != "Locked":
            messages.warning(request, "Students may not start peer review before activity lock is effective.")
    except:
        activity_lock = None
        messages.error(request, "You do not have an activity lock, students may not access peer review without an effective activity lock.")
         
    fields = ('title', 'description', 'max_mark', 'deleted',)
    MarkingSectionFormSet = modelformset_factory(MarkingSection, fields=fields, \
                                              formset=BaseMarkingSectionFormSet, \
                                              can_delete = False, extra = 10) 
    
    qset = MarkingSection.objects.filter(peer_review_component=peerreview_component, deleted=False)

    if request.method == 'POST':
        formset = MarkingSectionFormSet(request.POST, queryset=qset)
        form = AddPeerReviewComponentForm(class_size, request.POST)

        if not formset.is_valid(): 
            if formset.non_form_errors(): # not caused by error of an individual form
                error_info = formset.non_form_errors()[0]   
        elif form.is_valid() and formset.is_valid():
            peerreview_component.due_date = form.cleaned_data['due_date']
            peerreview_component.number_of_reviews = form.cleaned_data['number_of_reviews']
            peerreview_component.save()
            _save_marking_section(formset, peerreview_component)
            return HttpResponseRedirect(reverse('grades.views.activity_info', kwargs={'course_slug': course_slug, 'activity_slug': activity_slug}))
    else:
        formset = MarkingSectionFormSet(queryset = qset)
        form = AddPeerReviewComponentForm(class_size, initial=
        {
            'due_date':peerreview_component.due_date,
            'number_of_reviews':peerreview_component.number_of_reviews,
        })

    if error_info:
        messages.add_message(request, messages.ERROR, error_info)
    context = {
        'form' : form,
        'formset' : formset,
        'course' : course,
        'activity' : activity,
    }
    return render(request, "peerreview/edit_peer_review_component.html", context)

@requires_course_staff_by_slug
def staff_review_student(request, course_slug, activity_slug, userid):
    try:
        student_member = get_object_or_404(Member, person__userid=userid, offering__slug=course_slug)
        print "student found"
        print student_member.person.userid
    except:
        print "student not found"
    course = get_object_or_404(CourseOffering, slug = course_slug)
    activity = get_object_or_404(Activity, slug = activity_slug, offering=course)
    peer_review_component = get_object_or_404(PeerReviewComponent, activity = activity)
    
    # collect submission status
    sub_comps = [sc.title for sc in SubmissionComponent.objects.filter(activity=activity, deleted=False)]
    submitted = {}
    if activity.group:
        print "is group"
        subs = GroupSubmission.objects.filter(activity=activity).select_related('group')
        for s in subs:
            members = s.group.groupmember_set.filter(activity=activity)
            for m in members:
                submitted[m.student.person.userid] = True
    else:
        print "not group"
        subs = StudentSubmission.objects.filter(activity=activity)
        for s in subs:
            submitted[s.member.person.userid] = True

    try:
        received_reviews = StudentPeerReview.objects.filter(peer_review_component = peer_review_component, reviewee = student_member)
    except:
        pass
    try:
        given_reviews = StudentPeerReview.objects.filter(peer_review_component = peer_review_component, reviewer = student_member)
    except:
        pass
    
    context = {
        'student': student_member,
        'activity': activity,
        'course': course,
        'sub_comps': sub_comps,
        'submitted': submitted,
        'received_reviews': received_reviews,
        'given_reviews': given_reviews
    }
    
    return render(request, "peerreview/staff_review_student.html", context)
    
    
@requires_course_staff_by_slug
def peer_review_info_staff(request, course_slug, activity_slug):
    course = get_object_or_404(CourseOffering, slug=course_slug)
    activity = get_object_or_404(Activity, slug=activity_slug)
    
    # collect submission status
    sub_comps = [sc.title for sc in SubmissionComponent.objects.filter(activity=activity, deleted=False)]
    submitted = {}
    if activity.group:
        print "is group"
        subs = GroupSubmission.objects.filter(activity=activity).select_related('group')
        for s in subs:
            members = s.group.groupmember_set.filter(activity=activity)
            for m in members:
                submitted[m.student.person.userid] = True
    else:
        print "not group"
        subs = StudentSubmission.objects.filter(activity=activity)
        for s in subs:
            submitted[s.member.person.userid] = True
    
    try:
        peerreview = get_object_or_404(PeerReviewComponent, activity=activity)
    except:
        peerreview = None

    # build list of all students and grades
    students = Member.objects.filter(role="STUD", offering=activity.offering).select_related('person')
    received_reviews = []
    given_reviews = []
    if (peerreview):
        for student in students:
            try:
                received_reviews.append(len(StudentPeerReview.objects.filter(peer_review_component = peerreview, reviewee = student, feedback__gt='')))
            except:
                pass
            try:
                given_reviews.append(len(StudentPeerReview.objects.filter(peer_review_component = peerreview, reviewer = student, feedback__gt='')))
            except:
                pass

        combined = zip(students, received_reviews, given_reviews)
            
    context = {'course': course, 'activity': activity, 'students': combined, 'peerreview':peerreview, 'submitted':submitted, 'subs':subs}
    return render(request, 'peerreview/peer_review_info_staff.html', context)

@login_required
def peer_review_info_student(request, course_slug, activity_slug):
    student_member = get_object_or_404(Member, person__userid=request.user.username, offering__slug=course_slug, role='STUD')
    course = get_object_or_404(CourseOffering, slug = course_slug)
    activity = get_object_or_404(Activity, slug=activity_slug, offering=course)
    peerreview = get_object_or_404(PeerReviewComponent, activity=activity)
    student_member_list = Member.objects.filter(offering=course, role="STUD").exclude(pk=student_member.pk)
    try:
        activity_lock = ActivityLock.objects.get(activity=activity)
    except:
        activity_lock = None

    locked = is_student_locked(activity=activity, student=student_member)

    reviewer_components = []
    if activity_lock and locked:
        reviewer_components = list(StudentPeerReview.objects.filter(reviewer=student_member))
        if len(reviewer_components) < peerreview.number_of_reviews:
            submitted_students = []
            for student in student_member_list:
                sub, sub_component = get_current_submission(student.person, activity)
                if sub:
                    submitted_students.append(student)
            reviewer_components = generate_peerreview(peerreview=peerreview, students=submitted_students, student_member=student_member)
            
        if len(reviewer_components) == 0:
            messages.warning(request, "There doesn't seem to be any submission assigned to you for review, contact the instructor if this is not suppose to happen")

    reviewee_components = list(StudentPeerReview.objects.filter(reviewee=student_member))
    
    context = {
        'locked':locked,
        'activity_lock':activity_lock,
        'reviewer_components':reviewer_components,
        'reviewee_components':reviewee_components,
        'course':course,
        'activity':activity,
    }
    return render(request, "peerreview/student_peer_review.html", context)

@login_required
def student_review(request, course_slug, activity_slug, peerreview_slug):
    student_member = get_object_or_404(Member, person__userid=request.user.username, offering__slug=course_slug, role='STUD')
    course = get_object_or_404(CourseOffering, slug = course_slug)
    activity = get_object_or_404(Activity, slug=activity_slug, offering=course)
    peerreview = get_object_or_404(PeerReviewComponent, activity=activity)
    student_review = StudentPeerReview.objects.get(slug=peerreview_slug)
    
    submission, submitted_components = get_current_submission(student_review.reviewee.person, activity, include_deleted=False)
    
    if request.method == 'POST':
        form = StudentReviewForm(request.POST)
        if form.is_valid():
            student_review.feedback = form.cleaned_data['feedback']
            student_review.save()

            #send email notification to student
            student_review.add_reviewee_NewsItem()

        return HttpResponseRedirect(reverse('peerreview.views.peer_review_info_student', kwargs={'course_slug': course_slug, 'activity_slug': activity_slug}))
    else:
        form_initials = {
            'feedback' : student_review.feedback,
        }
        form = StudentReviewForm(initial=form_initials)

    context = {
        'submitted_components':submitted_components,
        'activity':activity,
        'course':course,
        'student_review':student_review,
        'form':form,
    }

    return render(request, "peerreview/student_review.html", context)

@login_required
def download_file(request, course_slug, activity_slug, component_slug, submission_id, peerreview_slug):
    course = get_object_or_404(CourseOffering, slug=course_slug)
    activity = get_object_or_404(course.activity_set, slug = activity_slug, deleted=False)
    student_review = get_object_or_404(StudentPeerReview, slug=peerreview_slug)
    peerreview = get_object_or_404(PeerReviewComponent, activity=activity)
    reviewer = student_review.reviewer
    reviewee = student_review.reviewee

    # make sure this user is allowed to see the file
    if request.user.username != reviewer.person.userid:
        return ForbiddenResponse
    elif not is_student_locked(student=reviewer, activity=activity) or not is_student_locked(student=reviewee, activity=activity):
        return ForbiddenResponse(request)
    
    # userid specified: get their most recent submission
    submission, submitted_components = get_current_submission(reviewee.person, activity, include_deleted=False)
    if not submission:
        return NotFoundResponse(request)

    # create the result
    if component_slug:
        # download single component if specified
        # get the actual component: already did the searching above, so just look in that list
        components = [sub for comp,sub in submitted_components if sub and sub.component.slug==component_slug]
        if not components:
            return NotFoundResponse(request)
        return components[0].download_response()
    else:
        # no component specified: give back the full ZIP file.
        return generate_zip_file(submission, submitted_components)


#code used for reference NOTE: delete later       
def _old_save_components(formset, activity, user):
    total_mark = 0
    for form in formset.forms:
        try:  # title is required, empty title triggers KeyError and don't consider this row
            form.cleaned_data['title']
        except KeyError:
            continue
        else:
            instance = form.save(commit = False)
            instance.numeric_activity = activity            
            instance.save()
            
            if not instance.deleted:
                total_mark += instance.max_mark
                action = 'saved'
            else:
                action = 'deleted'                           
            #LOG EVENT#
            l = LogEntry(userid=user,
                  description=(u"%s marking component %s of %s") % 
                              (action, instance, activity),
                  related_object=instance)  
            l.save()         
            
    return total_mark

def manage_activity_components(request, course_slug, activity_slug):    
    error_info = None
    course = get_object_or_404(CourseOffering, slug = course_slug)   
    activity = get_object_or_404(NumericActivity, offering = course, slug = activity_slug, deleted=False)   
    fields = ('title', 'description', 'max_mark', 'deleted',)
    ComponentsFormSet  = modelformset_factory(ActivityComponent, fields=fields, \
                                              formset=BaseActivityComponentFormSet, \
                                              can_delete = False, extra = 25) 
    
    qset = ActivityComponent.objects.filter(numeric_activity = activity, deleted=False)
                 
    if request.method == "POST":     
        formset = ComponentsFormSet(activity, request.POST, queryset = qset)
        
        if not formset.is_valid(): 
            if formset.non_form_errors(): # not caused by error of an individual form
                error_info = formset.non_form_errors()[0] 
        else:          
            # save the formset  
            now_max = _save_components(formset, activity, request.user.username)
            messages.add_message(request, messages.SUCCESS, 'Components of %s Saved!' % activity.name)
            # if the max grade changed
            if now_max != activity.max_grade: 
                old_max = activity.max_grade
                activity.max_grade = now_max
                activity.save()               
                messages.add_message(request, messages.WARNING, \
                                     "The max grade of %s updated from %s to %s" % (activity.name, old_max, now_max))
           
            return _redirct_response(request, course_slug, activity_slug)            
    else: # for GET request
        formset = ComponentsFormSet(activity, queryset = qset) 
    
    if error_info:
        messages.add_message(request, messages.ERROR, error_info)
    return render_to_response("marking/components.html", 
                              {'course' : course, 'activity' : activity,\
                               'formset' : formset },\
                               context_instance=RequestContext(request))

