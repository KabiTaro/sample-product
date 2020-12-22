from django.core.management.base import BaseCommand
from conoha.service import ConohaObjectStorage


class Command(BaseCommand):
    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument(
            'container_name',
            type=str,
            help='Please specify the name of the container you want to delete.'
        )

    def handle(self, *args, **options):
        conoha = ConohaObjectStorage.factory(
            container_name=options['container_name'])

        response = conoha.delete_container()
        self.stdout.write('{}:{}'.format(
            response.status_code, response.reason))
