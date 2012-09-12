from coredata.models import Semester, CourseOffering, Person, Member
from coredata.tests import create_offering
from courselib.testing import basic_page_tests

from datetime import date, datetime

from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client

from techreq.models import TechResource, TechRequirement
from settings import CAS_SERVER_URL


class ApplicationTest(TestCase):
    fixtures = ['test_data']
    #def setUp(self):

    def test_application(self):
        # set up course and related data
        s, c = create_offering()
        # get a prof
        prof = Person.objects.get(userid="ggbaker")
        m = Member(person=prof, offering=c, role="INST")
        m.save()

        # add a tech requirement
        techreq1 = TechRequirement(name="Visual Studio", course_offering=c, location="CSIL Windows")
        techreq1.save()

        # login the prof
        client = Client()
        client.login(ticket=prof.userid, service=CAS_SERVER_URL)  

        # get the tech requirement managing page
        url = reverse('techreq.views.manage_techreqs', kwargs={'course_slug': c.slug,})
        response = basic_page_tests(self, client, url)
        self.assertEqual(response.status_code, 200)
        # check that our manually added tech requirement is in the page
        self.assertContains(response, '<td>%s</td>' % (techreq1.name))

        # delete the requirement and check that the requirement is no longer on the page
        post_data = {
            'techreq_id':techreq1.id,
            'action':'del',
        }
        response = client.post(url, post_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, '<td>%s</td>' % (techreq1.name))

        # add a requirement using the form on the page
        # and check to see if you can find it on the new page
        post_data = {
            'name':'Eclipse',
            'location':'anywhere',
            'action':'add',
        }
        response = client.post(url, post_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<td>Eclipse</td>')