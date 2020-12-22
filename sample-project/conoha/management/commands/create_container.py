from django.core.management.base import BaseCommand
from conoha.service import ConohaObjectStorage


class Command(BaseCommand):
    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument(
            'container_name',
            type=str,
            help='Please specify the name of the container you want to create.'
        )
        parser.add_argument(
            '--read_acl',
            type=str,
            help='Set read acl.'
        )

    def handle(self, *args, **options):

        conoha = ConohaObjectStorage.factory(
            container_name=options['container_name'])
        optional_header = {'X-Container-Read': options['read_acl']}
        response = conoha.create_container(
            optional_header=optional_header
        )
        self.stdout.write('{}:{}'.format(
            response.status_code, response.reason))
