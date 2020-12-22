from api_v1.models import PostImage
from api_v1.serializers import ImageSerializer

from rest_framework.response import Response
from rest_framework import status, views
from rest_framework.permissions import AllowAny
from django.db import transaction
from conoha.exceptions import ConohaException


class ImageApiView(views.APIView):
    permission_classes = [AllowAny]

    # GET
    def get(self, request, *args, **kwargs):
        post_image = PostImage.objects.order_by('-reg_datetime')
        serializer = ImageSerializer(instance=post_image, many=True)
        return Response(serializer.data, status.HTTP_200_OK)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        serializer = ImageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            serializer.save()
        except ConohaException as e:
            return Response(
                data=e.args,
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(status=status.HTTP_201_CREATED)
