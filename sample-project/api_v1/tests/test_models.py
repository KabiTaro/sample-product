from api_v1.models import PostImage
import responses
from django.test import TestCase
import api_v1.tests.utils as test_utils
from django.conf import settings
from conoha.exceptions import ConohaUploadException

test_container = settings.IMAGE_CONTAINER


class Test_PostImage(TestCase):
    @responses.activate
    def test_upload_ok(self):
        responses.add(method=responses.POST,
                      url=test_container.identity_config.request_url,
                      json={'access':
                            {'token':
                             {'issued_at': '9999-12-31T23:59:59.999999',
                              'expires': test_utils.iso_format_datetime_str(
                                  delta_days=1),
                              'id': 'testtoken999999',
                              'tenant': {},
                              'serviceCatalog': []
                              }
                             }}, status=200)

        test_data = PostImage(image_extension="jpeg",
                              image_origin_name="test",
                              image_size=523)
        test_url = '{base_url}/{id}.jpeg'.format(
            base_url=test_container.request_url,
            id=test_data.id)

        responses.add(method=responses.PUT,
                      url=test_url,
                      status=200)
        test_data.save(image=test_utils.TEST_IMAGE)

        self.assertEquals(1, PostImage.objects.filter(id=test_data.id).count())

        responses.assert_call_count(test_url, 1)

    # アップロード失敗するケース
    @responses.activate
    def test_upload_ng(self):
        responses.add(method=responses.POST,
                      url=test_container.identity_config.request_url,
                      json={'access':
                            {'token':
                             {'issued_at': '9999-12-31T23:59:59.999999',
                              'expires': test_utils.iso_format_datetime_str(
                                  delta_days=1),
                              'id': 'testtoken999999',
                              'tenant': {},
                              'serviceCatalog': []
                              }
                             }}, status=200)

        test_data = PostImage(image_extension="jpeg",
                              image_origin_name="test",
                              image_size=523)
        test_url = '{base_url}/{id}.jpeg'.format(
            base_url=test_container.request_url,
            id=test_data.id)

        responses.add(method=responses.PUT,
                      url=test_url,
                      status=403)
        with self.assertRaises(ConohaUploadException):
            test_data.save(image=test_utils.TEST_IMAGE)

        self.assertEquals(0, PostImage.objects.filter(
            id=test_data.id).count())

        responses.assert_call_count(test_url, 1)
