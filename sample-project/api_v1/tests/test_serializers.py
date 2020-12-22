from django.test import TestCase
from api_v1.serializers import ImageSerializer
from rest_framework.serializers import ValidationError
import api_v1.tests.utils as test_utils
from api_v1.models import PostImage
from pytz import timezone
from django.conf import settings


class Test_ImageSerializer(TestCase):
    def setUp(self):
        self.test_data1 = PostImage.objects.create(
            image_extension="png",
            image_origin_name="test1",
            image_size=523
        )
        self.test_data2 = PostImage.objects.create(
            image_extension="jpeg",
            image_origin_name="test2",
            image_size=322
        )

    def test_validate_image_ok(self):
        test_data = {
            'image_origin_name': 'test',
            'image_content': test_utils.TEST_IMAGE
        }
        serializer = ImageSerializer(data=test_data)
        result = serializer.is_valid(raise_exception=True)
        self.assertTrue(result)
        expected_data = {
            'image_size': 220,
            'image_origin_name': 'test',
            'image_extension': 'png',
        }

        self.assertEquals(serializer.data, expected_data)

    def test_serialize_ok(self):
        _tz = timezone(settings.TIME_ZONE)
        post_image = PostImage.objects.order_by('-reg_datetime')
        serializer = ImageSerializer(instance=post_image, many=True)
        expected_dict = [

            {
                'image_url': self.test_data2.image_url,
                'image_size': self.test_data2.image_size,
                'image_origin_name': self.test_data2.image_origin_name,
                'image_extension': self.test_data2.image_extension,
                'reg_datetime': str(
                    self.test_data2.reg_datetime.astimezone(tz=_tz)
                )
                .split('.')[0]
            },
            {
                'image_url': self.test_data1.image_url,
                'image_size': self.test_data1.image_size,
                'image_origin_name': self.test_data1.image_origin_name,
                'image_extension': self.test_data1.image_extension,
                'reg_datetime': str(
                    self.test_data1.reg_datetime.astimezone(tz=_tz)
                )
                .split('.')[0]
            }
        ]

        self.assertEquals(serializer.data, expected_dict)

    # 必須項目をPostしていなかったケース
    def test_validate_required_ng(self):
        test_data = {
            'image_origin_name': 'testtesttest'
        }
        serializer = ImageSerializer(data=test_data)
        with self.assertRaisesMessage(
                expected_exception=ValidationError,
                expected_message='この項目は必須です。'):
            serializer.is_valid(raise_exception=True)

    # image_origin_nameが50文字超えるケース
    def test_validate_image_origin_name_ng(self):
        test_data = {
            'image_origin_name': 'testtesttest'
            'testtesttesttesttesttesttest'
            'testtesttesttesttesttesttest'
            'testtesttesttesttesttesttest'
            'testtesttesttesttesttesttest',
            'image_content': test_utils.TEST_IMAGE
        }
        serializer = ImageSerializer(data=test_data)
        with self.assertRaisesMessage(
                expected_exception=ValidationError,
                expected_message='この項目が50文字より長くならないようにしてください。'):
            serializer.is_valid(raise_exception=True)

    # image_contentがbase64形式でないケース
    def test_validate_image_ng(self):
        test_data = {
            'image_origin_name': 'test',
            'image_content': 'testtesttest'
        }
        serializer = ImageSerializer(data=test_data)
        with self.assertRaisesMessage(
                expected_exception=ValidationError,
                expected_message='無効なデータです。'):
            serializer.is_valid(raise_exception=True)

    # image_contentがbase64形式だが拡張子が違うケース
    def test_validate_image_extension_ng(self):
        test_data = {
            'image_origin_name': 'test',
            'image_content': 'data:image/bmp;base64,/9j/4'
        }
        serializer = ImageSerializer(data=test_data)
        with self.assertRaisesMessage(
                expected_exception=ValidationError,
                expected_message='無効な拡張子です。'):
            serializer.is_valid(raise_exception=True)

    # image_contentがbase64形式で且つ拡張子も期待された形式だが
    # デコードで失敗するケース
    def test_validate_image_decode_ng(self):
        test_data = {
            'image_origin_name': 'test',
            'image_content': 'data:image/jpeg;base64,/9j/4'
        }
        serializer = ImageSerializer(data=test_data)
        with self.assertRaisesMessage(
                expected_exception=ValidationError,
                expected_message='画像のデコードに失敗しました。'):
            serializer.is_valid(raise_exception=True)
