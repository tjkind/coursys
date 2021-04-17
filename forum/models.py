from coredata.models import Member, CourseOffering
from django.db import models
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.conf import settings
from courselib.json_fields import JSONField
from courselib.json_fields import getter_setter
from courselib.branding import product_name
from courselib.markup import ParserFor, ensure_sanitary_markup, markup_to_html
from autoslug import AutoSlugField
from courselib.slugs import make_slug
import datetime

THREAD_STATUSES = (
                  ('OPN', 'Open'),
                  ('ANS', 'Answered'),
                  ('CLO', 'Closed'),
                  ('HID', 'Hidden'),
                  )

THREAD_TYPES = [
    ('DFT', 'Default'),
    ('QUT', 'Question'),
]

def _time_delta_to_string(time):
    td = datetime.datetime.now() - time
    days, hours, minutes, seconds = td.days, td.seconds / 3600, (td.seconds / 60) % 60, td.seconds
    
    if days is 0:
        if hours is 0:
            if minutes is 0:
                return '%d seconds ago' % seconds
            elif minutes is 1:
                return '1 minute ago'
            else:
                return '%d minutes ago' % minutes
        elif hours is 1:
            return '1 hour ago'
        else:
            return '%d hours ago' % hours
    elif days is 1:
        return '1 day ago'
    elif days < 8:
        return '%d days ago' % days
    else:
        return time.strftime('%b %d, %Y')
    
class ForumThread(models.Model):
    """
    A thread associated with a CourseOffering
    """
    offering = models.ForeignKey(CourseOffering, null=False, on_delete=models.PROTECT)
    title = models.CharField(max_length=140, help_text="A brief description of the thread")
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity_at = models.DateTimeField(auto_now_add=True)
    reply_count = models.IntegerField(default=0)
    status = models.CharField(max_length=3, choices=THREAD_STATUSES, default='OPN', help_text="The thread status: Closed: no replies allowed, Hidden: cannot be seen")
    author = models.ForeignKey(Member, on_delete=models.PROTECT, related_name='author')
    thread_type = models.CharField(max_length=3, choices=THREAD_TYPES, default='DFT', help_text="The thread types: Default: No additional behaviour, Question: Request an instructor answer")

    endorsed_answer = models.ForeignKey('ForumReply', null=True, on_delete=models.SET_NULL)
    endorsed_by = models.ForeignKey(Member, null=True, on_delete=models.SET_NULL, related_name='endorsed_by')
    endorsed_on = models.DateTimeField(null=True)

    def autoslug(self):
        return make_slug(self.title)
    slug = AutoSlugField(populate_from='autoslug', null=False, editable=False, unique_with=['offering'])

    def save(self, *args, **kwargs):
        if self.status not in [status[0] for status in THREAD_STATUSES]:
            raise ValueError('Invalid thread status')

        super(ForumThread, self).save(*args, **kwargs)

        # TODO: handle subscriptions
        
    def get_absolute_url(self):
        return reverse('offering:forum:view_thread', kwargs={'course_slug': self.offering.slug, 'thread_slug': self.slug})

    def new_reply_update(self):
        self.last_activity_at = datetime.datetime.now()
        self.reply_count = self.reply_count + 1
        self.save()
        
    def last_activity_at_delta(self):
        return _time_delta_to_string(self.last_activity_at)
    
    def created_at_delta(self):
        return _time_delta_to_string(self.created_at)
        
    def __str___(self):
        return self.title
        

REPLY_STATUSES = (
                  ('VIS', 'Visible'),
                  ('HID', 'Hidden'),
                  )

class ForumReply(models.Model):
    """
    A reply to a Forum Thread
    """
    thread = models.ForeignKey(ForumThread, on_delete=models.CASCADE)
    parent = models.ForeignKey("self", on_delete=models.PROTECT, null=True)
    content = models.TextField(blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=3, choices=REPLY_STATUSES, default='VIS')
    author = models.ForeignKey(Member, on_delete=models.PROTECT)
    def autoslug(self):
        return make_slug(self.author.person.userid)
    slug = AutoSlugField(populate_from='autoslug', null=False, editable=False, unique_with=['thread'])
    config = JSONField(null=False, blank=False, default=dict)
        # p.config['markup']:  markup language used: see courselib/markup.py
        # p.config['math']: content uses MathJax? (boolean)
        # p.config['brushes']: used SyntaxHighlighter brushes (list of strings) -- no longer used with highlight.js
    
    defaults = {'math': False, 'markup': 'creole'}
    math, set_math = getter_setter('math')
    markup, set_markup = getter_setter('markup')
    #brushes, set_brushes = getter_setter('brushes')

    def save(self, *args, **kwargs):
        if self.status not in [status[0] for status in REPLY_STATUSES]:
            raise ValueError('Invalid reply status')
        if not self.pk:
            self.thread.new_reply_update()

        print("hey tor", args, kwargs)

        self.content = ensure_sanitary_markup(self.content, self.markup(), restricted=True)

        super(ForumReply, self).save(*args, **kwargs)

        # TODO: handle subscriptions

    def html_content(self):
        "Convert self.content to HTML"
        return markup_to_html(self.content, self.markup(), offering=self.thread.offering, html_already_safe=True,
                              restricted=True)
    
    def get_absolute_url(self):
        return self.thread.get_absolute_url() + '#reply-' + str(self.id)

    def to_dict(self):
        return {
            "author": self.author.person.userid,
            "thread": self.thread.title,
            "content": self.content,
            "visibility": self.get_status_display(),
            "created": str(self.created_at),
            "modified": str(self.modified_at)
        }
    
    def create_at_delta(self):
        return _time_delta_to_string(self.created_at)