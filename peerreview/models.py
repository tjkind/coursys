from autoslug import AutoSlugField
from courselib.slugs import make_slug
from django.db import models
from grades.models import Activity
from coredata.models import Member
from jsonfield import JSONField
import datetime
from random import randrange

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
    feedback = models.TextField(null=True, blank=True)
    submission_date = models.DateTimeField(default=datetime.datetime.now())
    identifier = models.CharField(max_length=32)

    def autoslug(self):
        return make_slug(self.identifier)
    slug = AutoSlugField(populate_from=autoslug, null=False, editable=False, unique=True)

    hidden = models.BooleanField(null=False, default=False)
    config = JSONField(null=False, blank=False, default={})

def generate_peerreview(peerreview, students, student_member, overlimit=False):
    review_components = list(StudentPeerReview.objects.filter(reviewer=student_member))
    number_of_reviews = peerreview.number_of_reviews
    student_pending = []
    priority_list = []

    for student in students:
        #check if student_member is already reviewing student's work
        if(StudentPeerReview.objects.filter(peer_review_component=peerreview, reviewer=student_member, reviewee=student)):
            continue
        else:
            reviewed_times = len(StudentPeerReview.objects.filter(reviewee=student))
            priority_list.append((student, reviewed_times))

    priority_list = sorted(priority_list, key=lambda student:student[1])

    for student, reviewed in priority_list:
        if (len(student_pending)+len(review_components)>=number_of_reviews):
            break
        elif reviewed>=number_of_reviews and not overlimit:
            break
        else:
            student_pending.append(student)

    if not overlimit and (len(student_pending)+len(review_components))<number_of_reviews:
        return None

    for student in student_pending:
        unique = False
        identifier = identifier_generator()
        while not unique:
            try:
                check_unique = StudentPeerReview.objects.get(peer_review_component=peerreview, identifier=identifier)
                identifier = identifier_generator()
            except:
                unique = True
        
        new_review = StudentPeerReview.objects.create(
            peer_review_component = peerreview,
            reviewer = student_member,
            reviewee = student,
            identifier = identifier,
        )
        review_components.append(new_review)

    return review_components

def identifier_generator():
    capletters = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
    letters = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
    vowels = ['a','e','i','o','u']

    first_name_length = randrange(3,14)
    last_name_length = randrange(2,14)

    name = ""
    for i in range(first_name_length):
        if i == 0:
            name += capletters[randrange(0,25)]
        elif i == 1:
            name += vowels[randrange(0,4)]
        elif i%4 == 0:
            name += vowels[randrange(0,4)]
        else:
            name += letters[randrange(0,25)]

    name += " "

    for i in range(last_name_length):
        if i == 0:
            name += capletters[randrange(0,25)]
        elif i == 1:
            name += vowels[randrange(0,4)]
        elif i%4 == 0:
            name += vowels[randrange(0,4)]
        else:
            name += letters[randrange(0,25)]

    return name