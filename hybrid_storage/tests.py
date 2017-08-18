from django.test import TestCase
from django.core.files import File
from django.conf import settings
from courselib.storage import UploadedFileStorage
from advisornotes.models import AdvisorNote
from coredata.models import Person, Unit
from hybrid_storage.models import FileInfo, FileData, FileWrite
import os
import six


FILEDATA = [
    b'first\ffile_contents',
    b'different\ncontents',
    b'yet\nmore\ncontents\nfor\ntesting',
]
LOCATIONS = list(settings.HYBRID_STORAGE_LOCATIONS)

class HybridStorageTest(TestCase):
    fixtures = ['basedata', 'coredata']

    def test_storage(self):
        student = Person.objects.get(userid='0aaa0')
        advisor = Person.objects.get(userid='dzhao')
        unit = Unit.objects.get(slug='cmpt')

        # manually create a file, imitating the legacy storage
        legacy_location = UploadedFileStorage._legacy_storage._location
        legacy_file = os.path.join(legacy_location, 'fa0.txt')
        with open(legacy_file, 'wb') as fh:
            fh.write(FILEDATA[0])

        # make sure it can be saved and retrieved
        legacy_note = AdvisorNote(text='foo', student=student, advisor=advisor, file_attachment='fa0.txt', file_mediatype='text/plain', unit=unit)
        legacy_note.save()
        legacy_notex = AdvisorNote.objects.get(id=legacy_note.id)
        self.assertEqual(FILEDATA[0], legacy_notex.file_attachment.read())

        # create a file using the HybridStorage
        note1 = AdvisorNote(text='foo', student=student, advisor=advisor, file_mediatype='text/plain', unit=unit)
        note1.file_attachment = File(six.BytesIO(FILEDATA[1]), name='fa1.txt')
        note1.save()
        # ... and make sure it comes back correctly.
        note1a = AdvisorNote.objects.get(id=note1.id)
        self.assertEqual(FILEDATA[1], note1a.file_attachment.read())
        self.assertEqual(FileInfo.objects.count(), 1)
        self.assertEqual(FileData.objects.count(), 1)
        self.assertEqual(FileWrite.objects.count(), 0)

        UploadedFileStorage.write_to_files(LOCATIONS[0])
        note2 = AdvisorNote(text='foo', student=student, advisor=advisor, file_mediatype='text/plain', unit=unit)
        note2.file_attachment = File(six.BytesIO(FILEDATA[2]), name='fa2.txt')
        note2.save()

        self.assertEqual(FileInfo.objects.count(), 2)
        self.assertEqual(FileData.objects.count(), 2)
        self.assertEqual(FileWrite.objects.count(), 1)

        n_loc = len(LOCATIONS)
        for loc in LOCATIONS[1:]:
            UploadedFileStorage.write_to_files(loc)

        # now: note1 file is in all locations; note2 file is in n-1 locations.
        self.assertEqual(FileInfo.objects.count(), 2)
        self.assertEqual(FileData.objects.count(), 2)
        self.assertEqual(FileWrite.objects.count(), 2*n_loc - 1)

        # can now purge note1 file from database; note2 file should remain
        UploadedFileStorage.purge_database_contents()
        self.assertEqual(FileInfo.objects.count(), 2)
        self.assertEqual(FileData.objects.count(), 1)
        self.assertEqual(FileWrite.objects.count(), n_loc - 1)

        note1b = AdvisorNote.objects.get(id=note1.id)
        self.assertEqual(FILEDATA[1], note1b.file_attachment.read())
        note2b = AdvisorNote.objects.get(id=note2.id)
        self.assertEqual(FILEDATA[2], note2b.file_attachment.read())

        os.remove(legacy_file)





