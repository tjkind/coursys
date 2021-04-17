from django.conf.urls import url
from courselib.urlparts import SLUG_RE
import forum.views as forum_views

forum_patterns = [ # prefix /COURSE_SLUG/forum/
    url(r'^$', forum_views.forum_index, name='forum_index'),
    url(r'^create_thread$', forum_views.create_thread, name='create_thread'),
    url(r'^thread/(?P<thread_slug>' + SLUG_RE + ')$', forum_views.view_thread, name='view_thread'),
    url(r'^thread/(?P<thread_slug>' + SLUG_RE + ')/endorse/(?P<reply_slug>' + SLUG_RE + ')$', forum_views.endorse_reply, name='endorse_reply'),
    url(r'^thread/(?P<thread_slug>' + SLUG_RE + ')/unendorse$', forum_views.unendorse_reply, name='unendorse_reply'),
]