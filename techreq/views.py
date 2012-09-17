from coredata.models import CourseOffering, Member
from courselib.auth import requires_global_role, requires_role, requires_course_staff_by_slug, ForbiddenResponse

from django.contrib import messages
from django.core.urlresolvers import reverse

from log.models import LogEntry

from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404

from techreq.models import TechRequirement
from techreq.forms import TechReqForm

@requires_course_staff_by_slug
def manage_techreqs(request, course_slug):
    course = get_object_or_404(CourseOffering, slug=course_slug)
    if not Member.objects.filter(offering=course, person__userid=request.user.username, role__in=["INST", "TA"]):
        return ForbiddenResponse(request, "Only instructors and TAs can manage course technical requirements")

    if request.method == 'POST' and 'action' in request.POST and request.POST['action']=='add':
        form = TechReqForm(course_offering=course, data=request.POST)
        if form.is_valid():
            t = TechRequirement(course_offering=form.course_offering, name=form.cleaned_data['name'], version=form.cleaned_data['version'], quantity=form.cleaned_data['quantity'], location=form.cleaned_data['location'], notes=form.cleaned_data['notes'])
            t.save()

            #LOG EVENT#
            l = LogEntry(userid=request.user.username, 
                description=("Tech Requirement added by instructor/TA: %s for %s") % (request.user.username, course),
                related_object=t)
            l.save()
            messages.success(request, 'Added %s as a Tech Requirement.' % (t.name))
            return HttpResponseRedirect(reverse(manage_techreqs, kwargs={'course_slug': course.slug}))
    elif request.method == 'POST' and 'action' in request.POST and request.POST['action']=='del':
        techreq_id = request.POST['techreq_id']
        techreqs = TechRequirement.objects.filter(id=techreq_id, course_offering=course)
        if techreqs:
            techreq = techreqs[0]
            techreq_name = techreq.name
            techreq.delete()
            #LOG EVENT#
            l = LogEntry(userid=request.user.username,
                description=("Tech Requirement removed by instructor/TA: %s for %s") % (request.user.username, course),
                related_object=techreq)
            l.save()
            messages.success(request, 'Removed the Tech Requirement %s.' % (techreq_name))
        return HttpResponseRedirect(reverse(manage_techreqs, kwargs={'course_slug': course.slug}))
    else:
        form = TechReqForm(course_offering=course)

    techreqs = TechRequirement.objects.filter(course_offering=course)
    context = {'course': course, 'techreqs': techreqs, 'form': form}
    return render_to_response('techreq/manage_techreqs.html', context, context_instance=RequestContext(request))

@requires_course_staff_by_slug
def edit_techreq(request, course_slug, techreq_id):
    course = get_object_or_404(CourseOffering, slug=course_slug)
    techreq = get_object_or_404(TechRequirement, id=techreq_id, course_offering=course)
    if not Member.objects.filter(offering=course, person__userid=request.user.username, role__in=["INST", "TA"]):
        return ForbiddenResponse(request, "Only instructors and TAs can manage course technical requirements")

    if request.method == 'POST' and 'action' in request.POST and request.POST['action']=='edit':
        form = TechReqForm(course_offering=course, data=request.POST)
        if form.is_valid():
            techreq.name = form.cleaned_data['name']
            techreq.version = form.cleaned_data['version']
            techreq.quantity = form.cleaned_data['quantity']
            techreq.location = form.cleaned_data['location']
            techreq.notes = form.cleaned_data['notes']
            techreq.save()

            #LOG EVENT#
            l = LogEntry(userid=request.user.username, 
                description=("Tech Requirement %s edited by instructor/TA: %s for %s") % (techreq.name, request.user.username, course),
                related_object=techreq)
            l.save()
            messages.success(request, 'Edited Tech Requirement "%s".' % (techreq.name))
            return HttpResponseRedirect(reverse(edit_techreq, kwargs={'course_slug': course.slug, 'techreq_id': techreq.id}))
    else:
        techreq_initial = {'name':techreq.name, 'version':techreq.version, 'quantity':techreq.quantity, 'location':techreq.location, 'notes':techreq.notes}
        form = TechReqForm(course_offering=course, initial=techreq_initial)

    context = {'course': course, 'techreq': techreq, 'form': form}
    return render_to_response('techreq/edit_techreq.html', context, context_instance=RequestContext(request))

#Test#
