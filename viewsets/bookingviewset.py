from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from taxi.permission import IsOwner

from taxi.models import User

from taxi.serializers.booking import BookingSerializer


class BookViewSet(viewsets.ModelViewSet):
    serializer_class = BookingSerializer
    http_method_names = ['get', 'post', 'delete']
    permission_classes = [IsAuthenticated, IsOwner]
    authentication_classes = [TokenAuthentication]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        data = {"code": "1", "message": " Booked Successfully ", "data": serializer.data}
        return Response(data, status=status.HTTP_201_CREATED)
