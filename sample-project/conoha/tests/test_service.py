import responses

from django.test import TestCase
import conoha.service as service
from conoha.exceptions import ConohaRequestsException, ConohaNotSpecifiedException
import api_v1.tests.utils as test_utils
from django.conf import settings
from dacite import from_dict

test_container = settings.IMAGE_CONTAINER


class TestConohaObjectStorage(TestCase):
    @responses.activate
    def test_is_set_token_ok(self):
        responses.add(method=responses.POST,
                      url=test_container.identity_config.request_url,
                      json={'access':
                            {'token':
                             {'issued_at': '2020-11-14T16:23:00.262864',
                              'expires': test_utils.iso_format_datetime_str(
                                  delta_days=1
                              ),
                              'id': 'testtoken999999',
                              'tenant': {},
                              'serviceCatalog': []
                              }
                             }}, status=200)
        test_container.identity_config.set_token()

        self.assertEquals(test_container.identity_config.res.id,
                          'testtoken999999')
        responses.assert_call_count(
            test_container.identity_config.request_url, 1)

    @responses.activate
    def test_is_set_token_ng(self):
        responses.add(method=responses.POST,
                      url=test_container.identity_config.request_url,
                      status=403)
        with self.assertRaises(ConohaRequestsException):
            test_container.identity_config.set_token()
        responses.assert_call_count(
            test_container.identity_config.request_url, 1)

    # 指定のステータスコード[429, 500, 502, 503, 504]でレスポンスが返ってきた際にリトライされるかどうか
    @responses.activate
    def test_retry_request_ok(self):
        status_code_list = [429, 500, 502, 503, 504]
        for i, status_code in enumerate(status_code_list):
            test_container_name = 'test_container{}'.format(i)
            test_container.object_storage_container = test_container_name
            responses.add(method=responses.PUT,
                          url=test_container.request_url,
                          status=status_code
                          )
            with self.subTest('status_code:{}'.format(status_code)):
                try:
                    test_container.create_container()
                except ConohaRequestsException as cre:
                    self.assertIs(True, cre.is_retry)

    # 指定のステータスコード[429, 500, 502, 503, 504]以外でレスポンスが返ってきた際にリトライされないかどうか
    @responses.activate
    def test_not_retry_request(self):
        status_code_list = [401, 403, 404, 506, 501, 505]
        for i, status_code in enumerate(status_code_list):
            test_container_name = 'test_container{}'.format(i)
            test_container.object_storage_container = test_container_name
            responses.add(method=responses.PUT,
                          url=test_container.request_url,
                          status=status_code
                          )
            with self.subTest('status_code:{}'.format(status_code)):
                try:
                    test_container.create_container()
                except ConohaRequestsException as cre:
                    self.assertIs(False, cre.is_retry)

    # トークンの有効期限が切れていた場合、再度トークンがセットされるか
    @responses.activate
    def test_objectstorage_is_reseted_token_ok(self):
        # 期限切れのトークンをセット
        test_container.identity_config.res = from_dict(
            data_class=service.ConohaIdentityres,
            data={
                'issued_at': '2020-11-14T16:23:00.262864',
                'expires': test_utils.iso_format_datetime_str(delta_days=-1),
                'id': 'old_testtoken'
            }
        )
        responses.add(method=responses.POST,
                      url=test_container.identity_config.request_url,
                      json={'access':
                            {'token':
                             {'issued_at': '2020-11-14T16:23:00.262864',
                              'expires': test_utils.iso_format_datetime_str(
                                  delta_days=1
                              ),
                              'id': 'new_testtoken',
                              'tenant': {},
                              'serviceCatalog': []
                              }
                             }}, status=200)
        responses.add(method=responses.PUT,
                      url=test_container.request_url,
                      status=200
                      )

        test_container.create_container()

        self.assertEquals(test_container.identity_config.res.id,
                          'new_testtoken')
        responses.assert_call_count(
            test_container.identity_config.request_url, 1)

    @responses.activate
    def test_not_secified_upload_object(self):
        responses.add(method=responses.PUT,
                      url=test_container.request_url,
                      status=200
                      )

        with self.assertRaisesMessage(
                expected_exception=ConohaNotSpecifiedException,
                expected_message='オブジェクト名が指定されていません'):
            test_container.upload_object(
                upload_image=None, upload_object_name=' ')
        responses.assert_call_count(
            test_container.request_url, 0)

    @responses.activate
    def test_not_secified_delete_object(self):
        responses.add(method=responses.DELETE,
                      url=test_container.request_url,
                      status=200
                      )

        with self.assertRaisesMessage(
                expected_exception=ConohaNotSpecifiedException,
                expected_message='オブジェクト名が指定されていません'):
            test_container.delete_object(delete_object_name=' ')
        responses.assert_call_count(
            test_container.request_url, 0)

    def test_not_secified_container_name(self):
        with self.assertRaisesMessage(
                expected_exception=ConohaNotSpecifiedException,
                expected_message='コンテナ名が指定されていません'):
            service.ConohaObjectStorage.factory(container_name=' ')