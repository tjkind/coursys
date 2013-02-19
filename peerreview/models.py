from django.db import models
from grades.models import Activity
from coredata.models import Member
from jsonfield import JSONField
import datetime

class PeerReviewComponent(models.Model):
    activity = models.ForeignKey(Activity)
    due_date = models.DateTimeField(null=True, help_text='Due date for Peer Reviews')
    number_of_reviews = models.IntegerField(null=True, help_text="This is the number of peer reviews each student is expected to perform")

    hidden = models.BooleanField(null=False, default=False)
    config = JSONField(null=False, blank=False, default={}) 

class StudentPeerReview(models.Model):
    peer_review_component = models.ForeignKey(PeerReviewComponent)
    reviewer = models.ForeignKey(Member, related_name="reviewer")
    reviewee = models.ForeignKey(Member, related_name="reviewee")
    feedback = models.TextField()
    submission_date = models.DateTimeField(default=datetime.datetime.now())
    identifier = models.CharField(max_length=32)

    hidden = models.BooleanField(null=False, default=False)
    config = JSONField(null=False, blank=False, default={}) 
