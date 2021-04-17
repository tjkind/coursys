from forum.models import ForumThread, ForumReply
from django import forms
from django.forms.widgets import TextInput
from courselib.markup import MarkupContentField, MarkupContentMixin
import genshi

class ForumReplyForm(MarkupContentMixin(field_name='content'), forms.ModelForm):
    content = MarkupContentField(label='Content', with_wysiwyg=True, restricted=True, rows=10)
    parent_id = forms.IntegerField(required=False, widget=forms.HiddenInput())
    class Meta:
        model = ForumReply
        exclude = ('thread', 'parent', 'created_at', 'modified_at', 'status', 'author', 'config')

class ForumThreadForm(forms.ModelForm):
    reply = MarkupContentField(label='Content', with_wysiwyg=True, restricted=True, rows=10)

    class Meta:
        model = ForumThread
        widgets = {'reply': ForumReplyForm, 'title': TextInput(attrs={'size': 60})}
        fields = ("title", "thread_type")
        help_texts = {
            'title': ('What is this thread about?'),
        }