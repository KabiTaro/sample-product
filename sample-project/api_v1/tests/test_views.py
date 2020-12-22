from rest_framework.test import APITestCase
import api_v1.tests.utils as test_utils
from rest_framework.serializers import ValidationError

from unittest.mock import patch, MagicMock, PropertyMock
from conoha.exceptions import ConohaUploadException

import json


class TestImageApiView(APITestCase):
    TARGET_URL = '/api/v1/post_image'

    def test_get_image_ok(self):
        response = self.client.get(path=self.TARGET_URL)

        self.assertEqual(response.status_code, 200)

    @patch('api_v1.views.ImageSerializer')
    def test_post_image_ok(self, ImageSerializerMock):
        test_data = {
            'image_origin_name': 'test',
            'image_content': test_utils.TEST_IMAGE
        }
        image_serializer = ImageSerializerMock()
        image_serializer.is_valid = MagicMock(
            return_value=True
        )

        image_serializer.save = MagicMock(return_value=None)

        response = self.client.post(
            path=self.TARGET_URL,
            data=test_data
        )

        image_serializer.is_valid.assert_called()
        image_serializer.save.assert_called()

        self.assertEqual(response.status_code, 201)

    @patch('api_v1.views.ImageSerializer')
    def test_post_image_ng(self, ImageSerializerMock):
        test_data = {
            'image_origin_name': 'test',
            'image_content': test_utils.TEST_IMAGE
        }
        image_serializer = ImageSerializerMock()
        image_serializer.is_valid = MagicMock(
            return_value=False,
            side_effect=ValidationError('Test_Exception')
        )
        image_serializer.is_valid.raise_exception = PropertyMock(
            return_value=True
        )

        response = self.client.post(
            path=self.TARGET_URL,
            data=test_data
        )

        res_content = json.loads(s=response.content)

        image_serializer.is_valid.assert_called()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(res_content, ["Test_Exception"])

    # Conohaオブジェクトストレージへの画像アップロードが失敗するケース
    @patch('api_v1.views.ImageSerializer')
    def test_post_image_upload_ng(self, ImageSerializerMock):
        test_data = {
            'image_origin_name': 'test',
            'image_content': test_utils.TEST_IMAGE
        }
        image_serializer = ImageSerializerMock()
        image_serializer.is_valid = MagicMock(
            return_value=True
        )
        image_serializer.save = MagicMock(
            return_value=None,
            side_effect=ConohaUploadException('画像のアップロードに失敗しました。')
        )
        response = self.client.post(
            path=self.TARGET_URL,
            data=test_data
        )

        res_content = json.loads(s=response.content)

        image_serializer.is_valid.assert_called()
        image_serializer.save.assert_called()

        self.assertEqual(response.status_code, 400)
        self.assertEqual(res_content, ['画像のアップロードに失敗しました。'])
