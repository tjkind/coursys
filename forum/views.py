from coredata.models import CourseOffering, Member
from courselib.auth import is_course_student_by_slug, is_course_staff_by_slug, ForbiddenResponse
from forum.models import ForumReply, ForumThread
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseForbidden, HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from featureflags.flags import uses_feature
from forum.forms import ForumThreadForm, ForumReplyForm
import datetime, itertools, json
from . import activity

def _get_course_and_view(request, course_slug):
    """
    Validates the request and returns the course object and view perspective ('student', 'staff')
    """
    course = get_object_or_404(CourseOffering, slug=course_slug)
    if not course.discussion() or course.discussion_version == 'OLD':
        raise Http404
    if is_course_student_by_slug(request, course_slug):
        return course, 'student'
    elif is_course_staff_by_slug(request, course_slug):
        return course, 'staff'
    else:
        return HttpResponseForbidden(), None

def _get_member(username, forum_view, course_slug):
    """
    Retrieves the Member object for a forum thread/reply
    """
    if forum_view is 'student':
        return Member.objects.filter(offering__slug=course_slug, person__userid=username, role="STUD", offering__graded=True).exclude(offering__component="CAN")[0]
    elif forum_view is 'staff':
        return Member.objects.filter(offering__slug=course_slug, person__userid=username, role__in=['INST', 'TA', 'APPR'], offering__graded=True).exclude(offering__component="CAN")[0]
    else:
        raise ValueError("Forum view type must be either 'student' or 'staff'")

@uses_feature('forum')
@login_required
def forum_index(request, course_slug):
    """
    Index page to view all forum threads
    """
    course, view = _get_course_and_view(request, course_slug)
    if view is None:
        # course is an HttpResponse in this case
        return course
    threads = ForumThread.objects.filter(offering=course).order_by('-last_activity_at')
    activity.update_last_viewed(_get_member(request.user.username, view, course_slug))
    paginator = Paginator(threads, 10)
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    try:
        threads = paginator.page(page)
    except (EmptyPage, InvalidPage):
        threads = paginator.page(paginator.num_pages)
    context = {'course': course, 'threads': threads, 'view': view, 'paginator': paginator, 'page': page}
    return render(request, 'forum/index.html', context)
    
@uses_feature('forum')
@login_required
def create_thread(request, course_slug):
    """
    Form to create a new forum thread
    """
    course, view = _get_course_and_view(request, course_slug)
    if view is None:
        # course is an HttpResponse in this case
        return course
    if request.method == 'POST':
        form = ForumThreadForm(data=request.POST)
        if form.is_valid():
            author = _get_member(request.user.username, view, course_slug)
            thread = form.save(commit=False)
            thread.offering = course
            thread.author = author
            thread.save()

            #Add content as first reply
            content = form.cleaned_data['reply']
            reply = ForumReply.objects.create(content=content[0], thread=thread, author=author)
            reply.config = {'markup': content[1], 'math': content[2]}
            reply.save()

            messages.add_message(request, messages.SUCCESS, 'Forum thread created successfully.')
            return HttpResponseRedirect(reverse('offering:forum:view_thread', kwargs={'course_slug': course_slug, 'thread_slug': thread.slug}))
    else:
        form = ForumThreadForm()
        print(form)
    return render(request, 'forum/create_thread.html', {'course': course, 'form': form})

def organize_replies(content, replies):
    top = { 'reply': content, 'children': [] }
    if replies.count() > 0:
        children = replies.filter(parent=content)
        new_replies = replies.exclude(id__in=children)
        for child in children:
            reply = organize_replies(child, new_replies)
            top['children'].append(reply)
    # print(top['reply'].content, top['children'])
    return(top)




@uses_feature('forum')
@login_required
def view_thread(request, course_slug, thread_slug):
    """
    Page to view a forum thread and reply
    """
    course, view = _get_course_and_view(request, course_slug)
    if view is None:
        # course is an HttpResponse in this case
        return course
    thread = get_object_or_404(ForumThread, slug=thread_slug, offering=course)
    if view == 'student' and thread.status == 'HID':
        raise Http404
    content = ForumReply.objects.filter(thread=thread, parent=None).first()

    if request.method == 'POST':
        if thread.status == 'CLO' and not view  == 'staff':
            raise Http404
        form = ForumReplyForm(data=request.POST)
        if form.is_valid():
            print("hey tor", form.cleaned_data)
            reply = form.save(commit=False)
            reply.thread = thread
            parent_id = form.cleaned_data['parent_id']
            if parent_id is None:
                reply.parent = content
            else:
                reply.parent = ForumReply.objects.get(id=parent_id)
            reply.author = _get_member(request.user.username, view, course_slug)
            reply.save()
            messages.add_message(request, messages.SUCCESS, 'Sucessfully replied')
            return HttpResponseRedirect(reverse('offering:forum:view_thread', kwargs={'course_slug': course_slug, 'thread_slug': thread.slug}))
    else:
        form = ForumReplyForm()
        replies = ForumReply.objects.filter(thread=thread, parent__isnull=False).order_by('created_at')
        organized_replies=organize_replies(content, replies)
    context = {'course': course, 'thread': thread, 'content': organized_replies, 'view': view, 'form': form,
               'username': request.user.username}
    return render(request, 'forum/thread.html', context)
