from django.db import models
from jsonfield import JSONField
from datetime import datetime
from coredata.models import Member
from grades.models import Activity

LOCK_STATUS_CHOICES = [
    ('locked', 'Lock'),
    ('unlocked', 'Unlock'),
    ('lock_pending', 'Unlocked Until')
]

class SubmissionLock(models.Model):
    """
        If a submission lock exists against a Member, this Member
        may not create or change a SubmittedComponent against
        this particular Activity.
    """
    member = models.ForeignKey(Member)
    activity = models.ForeignKey(Activity)
    status = models.CharField(max_length=20,choices=LOCK_STATUS_CHOICES,default='unlocked')
    created_date = models.DateTimeField(default=datetime.now())
    effective_date = models.DateTimeField(default=datetime.now())
    config = JSONField(null=False, blank=False, default={})

    class Meta:
        unique_together = (('member', 'activity'),)

class ActivityLock(models.Model):
    activity = models.ForeignKey(Activity)
    created_date = models.DateTimeField(default=datetime.now())
    effective_date = models.DateTimeField(default=datetime.now())
    config = JSONField(null=False, blank=False, default={})
