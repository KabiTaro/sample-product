from api_v1.models import PostImage
from rest_framework import serializers
from base64 import b64decode

BASE64_STR = ';base64,'

EXPECT_IMAGE_EXTENSION_LIST = ['jpg', 'png', 'jpeg']


class ImageSerializer(serializers.ModelSerializer):
    image_content = serializers.CharField(
        write_only=True, allow_null=False)
    reg_datetime = serializers.DateTimeField(
        format="%Y-%m-%d %H:%M:%S", required=False)

    class Meta:
        model = PostImage
        fields = (
            'image_url',
            'image_content',
            'image_size',
            'image_origin_name',
            'image_extension',
            'reg_datetime',
        )
        read_only_fields = ['image_url']

    def validate(self, data: dict):
        if BASE64_STR not in data['image_content']:
            raise serializers.ValidationError('無効なデータです。')

        ext, base64_encode_str = data['image_content'].split(BASE64_STR)
        extension = ext.split('/')[-1]
        if(extension not in EXPECT_IMAGE_EXTENSION_LIST):
            raise serializers.ValidationError(
                '無効な拡張子です。')

        try:
            image_data = b64decode(s=base64_encode_str)
        except BaseException as be:
            raise serializers.ValidationError(
                '画像のデコードに失敗しました。') from be
        data['image_content'] = image_data
        data['image_extension'] = extension
        data['image_size'] = len(image_data)
        return data

    def create(self, validated_data: dict):
        image_data = validated_data.pop('image_content')

        post_image = PostImage(**validated_data)

        post_image.save(image=image_data)

        return post_image
