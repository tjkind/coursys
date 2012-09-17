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

        # add a requirement and check to see if you can find it on the new page
        post_data = {
            'name':'Eclipse',
            'location':'anywhere',
            'action':'add',
        }
        response = client.post(url, post_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<td>Eclipse</td>')

        # add a second tech req to test the edit page
        techreq_orig_name = "Python"
        techreq_changed_name = "Python_alt"
        techreq2 = TechRequirement(name=techreq_orig_name, course_offering=c, location="CSIL Linux")
        techreq2.save()

        # get the tech requirement managing page
        url = reverse('techreq.views.manage_techreqs', kwargs={'course_slug': c.slug,})
        response = basic_page_tests(self, client, url)
        self.assertEqual(response.status_code, 200)
        # check that our manually added tech requirement is in the page, 
        # and it's alternate name is not(avoid false positives)
        self.assertContains(response, '<td>%s</td>' % (techreq_orig_name))
        self.assertNotContains(response, '<td>%s</td>' % (techreq_changed_name))

        # get the edit tech requirement page
        url = reverse('techreq.views.edit_techreq', kwargs={'course_slug': c.slug, 'techreq_id':techreq2.id})
        response = basic_page_tests(self, client, url)
        self.assertEqual(response.status_code, 200)
        # check that it has an input filled out with our techreqs name
        self.assertContains(response, '<input name="name" value="%s"' % (techreq_orig_name))
        self.assertNotContains(response, '<input name="name" value="%s"' % (techreq_changed_name))

        # edit the requirement and check that the requirement is changed on the edit page and the manage tech req page
        post_data = {
            'techreq_id':techreq2.id,
            'action':'edit',
            'name': techreq_changed_name,
            'location': techreq2.location,
            'quantity': "",
            'version': "",
            'notes': "",
        }
        response = client.post(url, post_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, '<input name="name" value="%s"' % (techreq_orig_name))
        self.assertContains(response, '<input name="name" value="%s"' % (techreq_changed_name))
        # check the manage page
        url = reverse('techreq.views.manage_techreqs', kwargs={'course_slug': c.slug,})
        response = basic_page_tests(self, client, url)
        self.assertEqual(response.status_code, 200)
        # check that our manually added tech requirement is in the page, 
        # and it's alternate name is not(avoid false positives)
        self.assertContains(response, '<td>%s</td>' % (techreq_changed_name))
        self.assertNotContains(response, '<td>%s</td>' % (techreq_orig_name))