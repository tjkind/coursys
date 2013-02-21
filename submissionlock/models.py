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

    def display_lock_date(self):
        if self.status == 'unlocked':
            return None
        if self.status == 'lock_pending':
            if self.activity.due_date == None:
                return None
            elif self.effective_date < self.activity.due_date:
                return None
        return self.effective_date

    def display_lock_status(self):
        if self.status == 'locked':
            return "Locked"
        elif self.status == 'lock_pending':            
            if self.activity.due_date == None:
                return "Unlocked"
            elif self.effective_date < self.activity.due_date:
                return "Unlocked"
            elif self.effective_date < datetime.now():
                return "Locked"
            else:
                return "Lock Pending"
        else:
            return "Unlocked"

class ActivityLock(models.Model):
    activity = models.ForeignKey(Activity)
    created_date = models.DateTimeField(default=datetime.now())
    effective_date = models.DateTimeField(default=datetime.now())
    config = JSONField(null=False, blank=False, default={})

    def display_lock_date(self):
        if self.activity.due_date == None:
            return None
        elif self.effective_date < self.activity.due_date:
            return None
        else:
            return self.effective_date

    def display_lock_status(self):
        if self.activity.due_date == None:
            return "Unlocked"
        elif self.effective_date < self.activity.due_date:
            return "Unlocked"
        elif self.effective_date > datetime.now():
            return "Lock Pending"
        else:
            return "Locked"

def is_student_locked(activity, student):
    locked = False
    try: #first check ActivityLock
        activity_lock = ActivityLock.objects.get(activity=activity)
    except:
        activity_lock = None

    #check ActivityLock and activity.due_date
    if activity_lock == None or activity.due_date == None:
        locked = False
    elif activity_lock.effective_date < activity.due_date:
        locked = False
    elif activity_lock.effective_date < datetime.now():
        locked = True

    try: #SubmissionLock has hierachy and will overshadow previous checks
        submission_lock = SubmissionLock.objects.get(activity=activity, member=student)
        if submission_lock.status == 'locked': #this will automatically return true because it's only set when student try to perform peer review and agreed to lock submissions
            return True
        elif submission_lock.status == 'lock_pending' and activity.due_date != None: #status "lock_pending" can only be set by the staff and therefore must taken into account the activity due date
            if submission_lock.effective_date < activity.due_date:
                locked = False
            elif submission_lock.effective_date < datetime.now():
                locked = True
            else:
                locked = False
        elif submission_lock.status == 'unlocked':
            locked = False
    except:
        pass
    return locked