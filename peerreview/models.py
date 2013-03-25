from autoslug import AutoSlugField
from courselib.slugs import make_slug
from django.db import models
from django.core.urlresolvers import reverse
from grades.models import Activity
from dashboard.models import *
from coredata.models import Member
from jsonfield import JSONField
import datetime
from random import randrange, shuffle, choice

class PeerReviewComponent(models.Model):
    activity = models.ForeignKey(Activity)
    due_date = models.DateTimeField(null=True, help_text='Due date for Peer Reviews')
    number_of_reviews = models.IntegerField(null=True, help_text="This is the number of peer reviews each student is expected to perform")

    hidden = models.BooleanField(null=False, default=False)
    config = JSONField(null=False, blank=False, default={}) 

class ReviewComponent(models.Model):
    peer_review_component = models.ForeignKey(PeerReviewComponent)
    max_mark = models.IntegerField(null=True, blank=True)
    title = models.CharField(max_length=50)
    description = models.TextField(null=True, blank=True)
    position = models.IntegerField()
    deleted = models.BooleanField(default=False)
    
    def autoslug(self):
        return make_slug(self.peer_review_component.activity.name + '-' + self.title)
    slug = AutoSlugField(populate_from=autoslug, null=False, editable=False, unique=True)
    config = JSONField(null=False, blank=False, default={})

class StudentReview(models.Model):
    review_component = models.ForeignKey(ReviewComponent)
    peer_review_component = models.ForeignKey(PeerReviewComponent)
    textbox = models.TextField()
    mark = models.IntegerField(null=True, blank=True)
    deleted = models.BooleanField(default=False)
    createdat = models.DateTimeField(default=datetime.datetime.now())
    lastmodified = models.DateTimeField()

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

    def add_reviewee_NewsItem(self):
        news = NewsItem.objects.create(
                    user = self.reviewee.person,
                    author = None,
                    course = self.peer_review_component.activity.offering,
                    source_app = 'peerreview',
                    title = "New review for %s " % (self.peer_review_component.activity.name),
                    content = 'To view the new review, click on the link provided',
                    url = reverse('peerreview.views.peer_review_info_student', kwargs={'course_slug': self.peer_review_component.activity.offering.slug, 'activity_slug': self.peer_review_component.activity.slug})
                )
        news.save()

def generate_peerreview(peerreview, students, student_member):
    review_components = list(StudentPeerReview.objects.filter(reviewer=student_member))
    number_of_reviews = peerreview.number_of_reviews
    student_pending = []

    priority_list = _generate_priority_list(students=students, student_member=student_member, peerreview=peerreview)

    for student, reviewed in priority_list:
        if (len(student_pending)+len(review_components)>=number_of_reviews):
            break
        else:
            student_pending.append(student)

    for student in student_pending:        
        new_review = StudentPeerReview.objects.create(
            peer_review_component = peerreview,
            reviewer = student_member,
            reviewee = student,
            identifier = _unique_identifier_generator(),
        )
        review_components.append(new_review)

    return review_components

def _generate_priority_list(students, student_member, peerreview):
    priority_list = []
    for student in students:
        #check if student_member is already reviewing student's work
        if len(StudentPeerReview.objects.filter(peer_review_component=peerreview, reviewer=student_member, reviewee=student))==0:
            reviewed_times = len(StudentPeerReview.objects.filter(reviewee=student))
            priority_list.append((student, reviewed_times))

    return sorted(priority_list, key=lambda student:student[1])

def _unique_identifier_generator():
    identifier = _name_generator() + " " + _name_generator()
    unique = False
    while not unique:
        try:
            check_unique = StudentPeerReview.objects.get(peer_review_component=peerreview, identifier=identifier)
            identifier = _name_generator() + " " + _name_generator()
        except:
            unique = True
    return identifier

def _name_generator():
    capletters = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
    letters = ['b','c','d','e','f','g','h','j','k','l','m','n','o','p','q','r','s','t','v','w','x','y','z']
    vowels = ['a','e','i','o','u']
    name_length = randrange(3,14)

    name = ""
    for i in range(name_length):
        if i == 0:
            name += choice(capletters)
        elif i == 1:
            name += choice(vowels)
        elif i%4 == 0:
            name += choice(vowels)
        else:
            name += choice(letters)
    return name