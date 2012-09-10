from django.db import models
from coredata.models import CourseOffering, Unit

class TechResource(models.Model):
	name = models.CharField(max_length=60, help_text='Name of the resource.')
	unit = models.ForeignKey(Unit)
	version = models.CharField(max_length=30, null=True, blank=True, help_text='Version of the resource, if applicable.')
	quantity = models.PositiveIntegerField(null=True, blank=True, help_text='Quantity of the resource, if applicable.')
	# Meeting times use CharFields for room/location so I'm copying that for now, 
	# we may need a more solid type for better requirement/resource location matching
	location = models.CharField(max_length=20, help_text='Location of the resource.')
	notes = models.TextField(null=True, blank=True, help_text='Any additional notes about the resource.')

	def __unicode__(self):
		return self.name

class TechRequirement(models.Model):
	name = models.CharField(max_length=60, help_text='Name of the requirement.')
	course_offering = models.ForeignKey(CourseOffering)
	version = models.CharField(max_length=30, null=True, blank=True, help_text='Version of the requirement, if applicable.')
	quantity = models.PositiveIntegerField(null=True, blank=True, help_text='Quantity of the requirement, if applicable.')
	# Meeting times use CharFields for room/location so I'm copying that for now, 
	# we may need a more solid type for better requirement/resource location matching
	location = models.CharField(max_length=20, help_text='Location where the requirement is required.')
	notes = models.TextField(null=True, blank=True, help_text='Any additional notes about the requirement.')
	satisfied_by = models.ForeignKey(TechResource, null=True, blank=True, help_text='The resource that satisfies this requirement.')