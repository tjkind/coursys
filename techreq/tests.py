from coredata.models import Semester, CourseOffering, Person, Member, Unit, Role
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
        # check that our manually added tech requirement is in the page, 
        # and it's alternate name is not(avoid false positives)
        self.assertContains(response, '<td>%s</td>' % (techreq_changed_name))
        self.assertNotContains(response, '<td>%s</td>' % (techreq_orig_name))



class ApplicationTechResourceTest(TestCase):
    fixtures = ['test_data']
    #def setUp(self):
    def test_application(self):
        tech = Person.objects.get(userid="dzhao")
        tech.save()

        u = Unit.objects.get(label="COMP")

        # add a tech resource
        techres1 = TechResource(name="Visual Studio", unit=u, location="CSIL Windows")
        techres1.save()

        # login the techstaff
        client = Client()
        client.login(ticket=tech.userid, service=CAS_SERVER_URL)  

        # get the tech resource managing page
        url = reverse('techreq.views.manage_techresources')
        response = basic_page_tests(self, client, url)
        self.assertEqual(response.status_code, 200)

        # check that our manually added tech resource in the page
        self.assertContains(response, '<td>%s</td>' % (techres1.name))

        # delete the resource and check that the resource is no longer on the page
        post_data = {
            'techresource_id':techres1.id,
            'action':'del',
        }
        response = client.post(url, post_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, '<td>%s</td>' % (techres1.name))


        # add a resource and check to see if you can find it on the new page
        post_data = {
            'name':'Eclipse',
            'location':'anywhere',
            'unit':u.id,
            'action':'add',
        }

        response = client.post(url, post_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<td>Eclipse</td>')

        # add a second tech resource to test the edit page
        techresource_orig_name = "Python"
        techresource_changed_name = "Python_alt"
        techres2 = TechResource(name=techresource_orig_name,  location="CSIL Linux", unit=u)
        techres2.save()

        # get the tech resource managing page

        url = reverse('techreq.views.manage_techresources')
        response = basic_page_tests(self, client, url)
        self.assertEqual(response.status_code, 200)

        # check that our manually added tech resource is in the page, 
        # and it's alternate name is not(avoid false positives)
        self.assertContains(response, '<td>%s</td>' % (techresource_orig_name))
        self.assertNotContains(response, '<td>%s</td>' % (techresource_changed_name))

        # get the edit tech resource page
        url = reverse('techreq.views.edit_techresources', kwargs={'techresource_id':techres2.id})
        response = basic_page_tests(self, client, url)

        self.assertEqual(response.status_code, 200)
        # check that it has an input filled out with our techres name
        self.assertContains(response, '<input id="id_name" type="text" name="name" value="%s"' % (techresource_orig_name))
        self.assertNotContains(response, '<input id="id_name" type="text" name="name" value="%s"' % (techresource_changed_name))

        # edit the res and check that the res is changed on the edit page and the manage tech res page
        post_data = {
            'techresource_id':techres2.id,
            'action':'edit',
            'name': techresource_changed_name,
            'location': techres2.location,
            'quantity': "",
            'version': "",
            'unit':u.id,
            'notes': "",
        }
        response = client.post(url, post_data, follow=True)
        self.assertEqual(response.status_code, 200)

        # go back to the manage page
        url = reverse('techreq.views.manage_techresources')
        response = basic_page_tests(self, client, url)
        self.assertEqual(response.status_code, 200)

        # check that our manually added tech techresource is in the page, 
        self.assertContains(response, '<td>%s</td>' % (techresource_changed_name))
        self.assertNotContains(response, '<td>%s</td>' % (techresource_orig_name))





