from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from hybrid_storage.models import FileInfo, FileWrite
import importlib


class Command(BaseCommand):
    help = 'Write HybridStorage files that are currently in the database to the local filesystem.'

    def add_arguments(self, parser):
        parser.add_argument('storage')

    def handle(self, *args, **options):
        location = settings.HYBRID_STORAGE_THIS_LOCATION
        module_name, class_name = options['storage'].rsplit('.', 1)
        module = importlib.import_module(module_name)
        storage = getattr(module, class_name)

        storage.write_to_files(location)
        storage.purge_database_contents()