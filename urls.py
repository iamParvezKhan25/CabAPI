from django.urls import path, include
from rest_framework import routers

from taxi.viewsets.userviewset import UserViewSet, CardViewSet
from taxi.viewsets.bookingviewset import BookViewSet


router = routers.DefaultRouter()
router.register(r'taxi', UserViewSet, basename='user')
router.register(r'card', CardViewSet, basename='card')
router.register(r'book', BookViewSet, basename='book')

urlpatterns = [
    path('api/v1/', include(router.urls)),
]