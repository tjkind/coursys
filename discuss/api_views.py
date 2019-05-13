from rest_framework import generics
from courselib.rest import APIConsumerPermissions, IsOfferingMember
from .models import DiscussionTopic, DiscussionMessage
from .serializers import DiscussionTopicSerializer, DiscussionMessageSerializer


class DiscussionTopics(generics.ListAPIView):
    permission_classes = (APIConsumerPermissions, IsOfferingMember,)
    consumer_permissions = set(['courses'])
    serializer_class = DiscussionTopicSerializer

    def get_queryset(self):
        # TODO: honour hidden status
        topics = DiscussionTopic.objects.filter(offering=self.offering).order_by('-pinned', '-last_activity_at')
        return topics


class DiscussionMessages(generics.ListAPIView):
    permission_classes = (APIConsumerPermissions, IsOfferingMember,)
    consumer_permissions = set(['courses'])
    serializer_class = DiscussionMessageSerializer

    def get_queryset(self):
        # TODO: honour hidden status on topic & messages
        replies = DiscussionMessage.objects \
            .filter(topic__offering=self.offering, topic__slug=self.kwargs['topic_slug']) \
            .order_by('created_at')
        return replies
