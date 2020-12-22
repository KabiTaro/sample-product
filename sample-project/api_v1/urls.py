from django.urls import path
from api_v1 import views

urlpatterns = [
    path('post_image', views.ImageApiView.as_view()),
]
