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
        # widgets = {'parent_id': forms.HiddenInput()}
        exclude = ('thread', 'parent', 'created_at', 'modified_at', 'status', 'author', 'config')

class ForumThreadForm(forms.ModelForm):
    title = forms.CharField(widget=TextInput(attrs={'size': 60}), help_text="What is this thread about?")
    reply = MarkupContentField(label='Content', with_wysiwyg=True, restricted=True, rows=10)

    class Meta:
        model = ForumThread
        widgets = {'reply': ForumReplyForm}
        exclude = ('offering', 'last_activity_at', 'created_at', 'reply_count', 'author', 'status', 'pinned')