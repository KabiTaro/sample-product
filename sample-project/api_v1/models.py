from django.db import models
from django.conf import settings
from uuid import uuid4
from conoha.exceptions import ConohaRequestsException, ConohaUploadException


class PostImage(models.Model):
    """投稿画像"""
    class Meta:
        db_table = 'post_iamge'

    # pk,オブジェクトストレージにファイルを格納する際の命名はid+image_extension
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    # バイト数
    image_size = models.BigIntegerField(verbose_name='画像サイズ', null=True)
    # リクエストされた画像の元の名称
    image_origin_name = models.CharField(
        verbose_name='画像元名', max_length=50, null=True)
    # オブジェクトストレージに格納したファイルの拡張子
    image_extension = models.CharField(
        verbose_name='画像拡張子', max_length=10, null=True)

    # オブジェクトストレージに格納したファイルの登録日時
    reg_datetime = models.DateTimeField(
        verbose_name='作成日時', auto_now_add=True, null=True)

    # オブジェクトストレージに格納したファイルのURL
    @property
    def image_url(self) -> str:
        return '{url}/{id}.{extension}'.format(
            url=settings.IMAGE_CONTAINER.request_url,
            id=self.id,
            extension=self.image_extension
        )

    # 保存時にConohaのオブジェクトストレージにファイルを格納
    def save(self, image: bytes = None, *args, **kwargs) -> None:
        if(image):
            try:
                settings.IMAGE_CONTAINER.upload_object(
                    upload_image=image,
                    upload_object_name='{id}.{extension}'.format(
                        id=str(self.id), extension=self.image_extension)
                )
            except ConohaRequestsException as ce:
                raise ConohaUploadException('画像のアップロードに失敗しました。') from ce
        super().save(*args, **kwargs)
