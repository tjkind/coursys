from django.core.files.storage import Storage, _possibly_make_aware
from django.core.exceptions import SuspiciousOperation
from django.core.files import File
from django.conf import settings
from django.db import transaction
from django.utils._os import abspathu, safe_join
import six
import errno
import hashlib
import itertools
import os.path
import re
import posixpath

from .models import FileInfo, FileData, LegacyFileInfo, FileWrite

# What's stored as the FileField name in the database is FileInfo(pk)/filename.ext. That lets code that expects a
# path as the .name to discover the true filename, and lets us find the FileInfo object.
name_pk_re = re.compile(r'^FileInfo\((\d+)\)/')


class HybridStorage(Storage):
    file_name_charset = getattr(settings, 'STORAGE_FILE_NAME_CHARSET', 'utf-8')
    _file_permissions_mode = getattr(settings, 'FILE_UPLOAD_PERMISSIONS', 0o0600) or 0o0600
    _directory_permissions_mode = getattr(settings, 'FILE_UPLOAD_DIRECTORY_PERMISSIONS)', 0o0700) or 0o0700

    def __init__(self, storage_id, location=None, legacy_storage=None, file_permissions_mode=None, directory_permissions_mode=None):
        self.storage_id = storage_id
        self.location = abspathu(location) or settings.MEDIA_ROOT
        self.file_permissions_mode = file_permissions_mode or HybridStorage._file_permissions_mode
        self.directory_permissions_mode = directory_permissions_mode or HybridStorage._directory_permissions_mode
        self._legacy_storage = legacy_storage

    # borrowed from django-storages s3boto3
    def _clean_name(self, name):
        """
        Cleans the name so that Windows style paths work
        """
        # Normalize Windows style paths
        clean_name = posixpath.normpath(name).replace('\\', '/')

        # os.path.normpath() can strip trailing slashes so we implement
        # a workaround here.
        if name.endswith('/') and not clean_name.endswith('/'):
            # Add a trailing slash as it was stripped.
            clean_name += '/'
        return clean_name

    # borrowed from django-storages s3boto3
    def _normalize_name(self, name):
        """
        Normalizes the name so that paths like /path/to/ignored/../something.txt
        work. We check to make sure that the path pointed to is not outside
        the directory specified by the LOCATION setting.
        """
        try:
            return safe_join(self.location, name)
        except ValueError:
            raise SuspiciousOperation("Attempted access to '%s' denied." % name)


    def _generate_hash(self, data):
        h = hashlib.sha256(data)
        return 'sha256:' + h.hexdigest()

    def _get_fileinfo(self, name):
        m = name_pk_re.match(name)
        if m:
            fi = FileInfo.objects.get(pk=m.group(1))
            return fi
        else:
            return LegacyFileInfo(path=name, storage=self._legacy_storage)

    def exists(self, name):
        return False

    def size(self, name):
        fi = self._get_fileinfo(name)
        return fi.size

    def _save(self, name, content):
        cleaned_name = self._clean_name(name)
        name = self._normalize_name(cleaned_name)
        filename = os.path.split(name)[1]
        data = content.read()
        with transaction.atomic():
            fd = FileData(data=data)
            fd.save()
            fi = FileInfo(storage_id=self.storage_id, filename=filename, content_hash=self._generate_hash(data),
                          size=len(content), filedata=fd, filepath=None)
            fi.save()

        return 'FileInfo(%i)/%s' % (fi.pk, filename)

    def _open(self, name, mode):
        fi = self._get_fileinfo(name)
        if isinstance(fi, LegacyFileInfo):
            # file in legacy non-hybrid Storage system
            return fi.open(mode)
        elif fi.filedata_id:
            # file contents in database
            fd = fi.filedata
            data = six.binary_type(fd.data)
        elif fi.filepath:
            # file contents on disk
            data = open(os.path.join(self.location, fi.filepath), mode).read()
        else:
            raise ValueError('FileInfo has neither filedata_id or filepath set.')

        if fi.content_hash != self._generate_hash(data):
            raise ValueError("Content has doesn't match content on disk.")

        return File(six.BytesIO(data))

    def path(self, name):
        raise NotImplementedError("This backend doesn't support absolute paths.")

    def delete(self, name):
        raise NotImplementedError("This backend does not support file deletion.")

    def listdir(self, path):
        raise NotImplementedError('This backend does not provide directory listings.')

    def url(self, name):
        raise NotImplementedError('This backend does not provide static URLs.')

    def get_accessed_time(self, name):
        raise NotImplementedError('This backend does not track access times.')

    def get_created_time(self, name):
        fi = self._get_fileinfo(name)
        return _possibly_make_aware(fi.created)

    def get_modified_time(self, name):
        return self.get_created_time(name)

    def write_to_files(self, location):
        """
        Write files to the local disk.
        """
        infos = FileInfo.objects.filter(filedata__isnull=False, storage_id=self.storage_id)
        file_writes = FileWrite.objects.filter(location=location, fileinfo__in=infos).select_related('fileinfo')
        already_written = {fw.fileinfo for fw in file_writes}
        need_writing = [fi for fi in infos if fi not in already_written]

        for fi in need_writing:
            self.write_to_file(fi, location)

    def write_to_file(self, fi, location):
        """
        Write this file to the local disk, which is known by the label "location".
        """
        assert isinstance(fi, FileInfo)
        assert fi.filedata

        storage_location = self.location
        dir_mode = self.directory_permissions_mode
        file_mode = self.file_permissions_mode

        dest_path, dest_filename = os.path.split(fi.filepath)
        dest_path = os.path.join(storage_location, dest_path)
        dest = os.path.join(dest_path, dest_filename)
        data = fi.filedata.data

        try:
            os.makedirs(dest_path, mode=dir_mode)
        except OSError as e:
            # ignore "directory exists" errors
            if e.errno != errno.EEXIST:
                raise

        #print('Writing as %s to %s' % (location, dest,))
        with open(dest, 'wb') as outfh:
            outfh.write(data)

        os.chmod(dest, file_mode)

        FileWrite.objects.get_or_create(fileinfo=fi, location=location)

    def purge_database_contents(self):
        """
        Purge FileData from database where it is no longer needed (i.e. has been written to all locations).
        """
        all_locations = set(settings.HYBRID_STORAGE_LOCATIONS)
        assert len(all_locations) > 0
        infos = FileInfo.objects.filter(filedata__isnull=False, storage_id=self.storage_id)
        file_writes = FileWrite.objects.filter(fileinfo__in=infos).order_by('fileinfo_id').select_related('fileinfo')
        for fi, writes in itertools.groupby(file_writes, lambda fw: fw.fileinfo):
            written_to = {fw.location for fw in writes}
            if all_locations <= written_to:
                # the corresponding FileData has been written everywhere and can be purged
                with transaction.atomic():
                    FileData.objects.get(id=fi.id).delete()
                    FileWrite.objects.filter(fileinfo=fi).delete()
                    fi.filedata = None
                    fi.save()
