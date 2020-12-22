from django.core.management.base import BaseCommand
from conoha.service import ConohaObjectStorage
from os import path, listdir
from django.conf import settings


class Command(BaseCommand):
    def handle(self, *args, **options):
        SITE_ROOT = settings.BASE_DIR

        COVERAGE_PATH = path.join(SITE_ROOT, 'coverage')

        if (not path.exists(path=COVERAGE_PATH)):
            raise FileNotFoundError()

        conoha = ConohaObjectStorage.factory(
            container_name=settings.COVERAGE_CONTAINER
        )

        for _file in listdir(COVERAGE_PATH):
            file_path = path.join(COVERAGE_PATH, _file)
            if path.isdir(file_path):
                break
            with open(file_path, 'rb') as f:
                file_byte = f.read()
                response = conoha.upload_object(
                    upload_image=file_byte,
                    upload_object_name=_file
                )
                self.stdout.write('[{file}] {status_code}:{msg}'.format(
                    file=_file,
                    status_code=response.status_code,
                    msg=response.reason
                )
                )
