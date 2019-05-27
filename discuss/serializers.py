from rest_framework import serializers
from django.urls import reverse
from django.conf import settings
from .models import DiscussionTopic, DiscussionMessage


class DiscussionTopicSerializer(serializers.ModelSerializer):
    content_html = serializers.SerializerMethodField()
    math = serializers.SerializerMethodField()
    link = serializers.SerializerMethodField()
    author = serializers.SerializerMethodField()

    class Meta:
        model = DiscussionTopic
        fields = ('title', 'content_html', 'pinned', 'last_activity_at', 'author', 'created_at', 'math', 'link', 'slug')

    def get_content_html(self, topic):
        return topic.html_content()

    def get_author(self, topic):
        return topic.author.person.name()

    def get_math(self, topic):
        return topic.math()

    def get_link(self, topic):
        # imitate HyperlinkCollectionField, which only allows one lookup field
        return (settings.BASE_ABS_URL
                + reverse('api:DiscussionMessages',
                          kwargs={'course_slug': topic.offering.slug, 'topic_slug': topic.slug})
                )


class DiscussionMessageSerializer(serializers.ModelSerializer):
    content_html = serializers.SerializerMethodField()
    math = serializers.SerializerMethodField()

    class Meta:
        model = DiscussionMessage
        fields = ('content_html', 'math', 'slug')

    def get_content_html(self, msg):
        return msg.html_content()

    def get_math(self, topic):
        return topic.math()
