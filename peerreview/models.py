from django.db import models
from grades.models import Activity
from coredata.models import Member
from jsonfield import JSONField
import datetime

class PeerReviewComponenet(models.Model):
    activity = models.ForeignKey(Activity)
    due_date = models.DateTimeField(null=True, help_text='Activity due date')
    number_reviews = models.IntegerField(null=True)

class StudentPeerReview(models.Model):
    peer_review_component = models.ForeignKey(PeerReviewComponenet)
    reviewer = models.ForeignKey(Member, related_name="reviewer")
    reviewee = models.ForeignKey(Member, related_name="reviewee")
    feedback = models.TextField()
    date = models.DateTimeField(default=datetime.datetime.now())
    identifier = models.CharField(max_length=32)
    config = JSONField(null=False, blank=False, default={}) 