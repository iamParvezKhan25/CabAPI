from django.contrib.auth import login, logout
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from taxi.permission import IsOwner
from taxi.utils import GenerateOtp

from taxi.models import User, Card
from rest_framework.authtoken.models import Token

from taxi.serializers.register import RegisterSerializer
from taxi.serializers.card import CardSerializer
from taxi.serializers.auth_serializer import OtpSerializer, LoginSerializer, ResendOtpSerializer, \
    UpdateUserSerializer, ChangePasswordSerializer, ResetPasswordSerializer, \
    UserProfileSerialization
from taxi.serializers.user_serializer import UserSeriailzer


class UserViewSet(viewsets.ModelViewSet):
    """
    A UserViewSet will provide API related to Login, Logout.
    """
    model = User
    queryset = model.objects.all()
    serializer_class = UserSeriailzer
    http_method_names = ['get', 'post', 'patch']
    authentication_classes = [TokenAuthentication]

    @action(detail=False, methods=['post'], serializer_class=RegisterSerializer)
    def register(self, request, *args, **kwargs):
        """
        This API is for sign up method will valid sign up credentials.
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        print(request.data)
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # # checking is user token already exists
        # Token.objects.create(user=user)
        # token = Token.objects.get(user=user)

        # email_body = 'Hi ' + user.username + 'this mail is system generated. Becuase you just sign up in new app
        # name ' \ 'MY BATHROOM APP. '
        # data = {'email_body': email_body, 'to_email': user.email, 'email_subject':
        # f'Welcome, {user.first_name} to MY Account APP.'} Util.send_email(data)

        user_serializer = UserSeriailzer(user)
        data = {'code': '1', 'message': 'Register Sucessfully!!! Otp Verification Need...',
                'data': user_serializer.data}
        return Response(data)

    @action(detail=False, methods=['post'], serializer_class=OtpSerializer)
    def otp(self, request):
        serializer = self.get_serializer(data=request.data)
        print(self.request.META.get('HTTP_ID'))
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        login(request, user)
        Token.objects.create(user=user)

        token = Token.objects.get(user=user)
        user_serializer = UserSeriailzer(user)
        data = dict()
        data['code'] = '1'
        data['message'] = 'Sucessfully Login!!!'
        data['data'] = user_serializer.data
        data['data']['token'] = token.key
        return Response(data)

    # @action(detail=False, methods=['POST'], serializer_class=ResendOtpSerializer)
    @action(detail=False, methods=['post'])
    def resend_otp(self, request, *args, **kwargs):
        """
        This method will valid login credentials and generate token.
        :param request:
        :param args:
        :param kwargs:
        :return:
        """

        user_id = self.request.META.get('HTTP_ID')
        otp = GenerateOtp.generateOTP()
        user = User.objects.get(id=user_id)

        if user.otp_verified == 0:
            user.otp = otp
            user.save()
            data = {'code': '1', 'message': 'Otp resend successfully'}

        else:
            data = {'code': '0', 'message': 'Your Account is Alredy Verified'}

        return Response(data)
        # serializer = self.serializer_class(data=request.data)
        # serializer.is_valid(raise_exception=True)
        # user = serializer.save()
        #
        # user_serializer = UserSeriailzer(user)
        # data = dict()
        # data['data'] = user_serializer.data
        # data['code'] = '1'
        # data['message'] = 'Otp Resend Sucessfully!!!'
        # return Response(data)

    @action(detail=False, methods=['post'], serializer_class=LoginSerializer)
    def login(self, request, *args, **kwargs):
        """
        This method will valid login credentials and generate token.
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        login(request, user)

        # checking is user token already exists
        token = Token.objects.filter(user=user)
        if not token:
            Token.objects.create(user=user)
        token = Token.objects.get(user=user)
        # print(token.key)
        user_serializer = UserSeriailzer(user)
        data = dict()
        data['data'] = user_serializer.data
        data['data']['token'] = token.key
        return Response({'code': '1', 'message': 'Succesfully User Login!!!!', 'data': data}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def logout(self, request):
        """
        This method will logout signed user and delete token.
        :param request:
        :return:
        """
        # user = User.objects.get(id=request.user.id)
        token = Token.objects.get(user=request.user.id)
        # print(user)  # Get Login User Details
        # print("TOKEN = " + token.key)  # Get Login User Token
        Token.objects.get(user=request.user.id).delete()
        logout(request)
        return Response({'code': '1', 'message': 'Sucessfully Logout!!!!!!'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['patch'], serializer_class=UpdateUserSerializer,
            permission_classes=[IsAuthenticated])
    def update_profile(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_old_data = request.user
        user_new_data = serializer.validated_data
        user = serializer.update(user_old_data, user_new_data)
        data = UpdateUserSerializer(user).data
        return Response({'code': '1', 'message': 'Your account is updated .', 'data': data}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['patch'], serializer_class=ChangePasswordSerializer,
            permission_classes=[IsAuthenticated])
    def change_password(self, request, *args, **kwargs):
        """
        API for change password of user.
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        login(request, user)
        token = Token.objects.get(user=user)
        user_serializer = UserSeriailzer(user)
        # print("TOKEN = " + token.key)
        data = dict()
        data['code'] = '1'
        data['message'] = 'Your password change successfully'
        data['data'] = user_serializer.data
        data['data']['token'] = token.key
        return Response(data)
        # return Response({'code': 1, 'message': 'Your password change successfully', 'data': data}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['patch'], serializer_class=ResetPasswordSerializer)
    def reset_password(self, request, *args, **kwargs):
        """
        This API for reset password.
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        user_serializer = UserSeriailzer(user)
        data = user_serializer.data

        return Response({'code': 1, 'message': 'Reset Password sent successfully!!!', 'data': data},
                        status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], serializer_class=UserProfileSerialization,
            permission_classes=[IsAuthenticated])
    def get_user_profile(self, request, *args, **kwargs):
        serializer = self.serializer_class(request.user)
        return Response({'code': '1', 'message': 'Succesfully User Details!!!!', 'data': serializer.data},
                        status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], serializer_class=CardSerializer,
            permission_classes=[IsAuthenticated])
    def add_card(self, request, *args, **kwargs):
        """
        API for change password of user.
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        card = serializer.save()
        card = CardSerializer(card)
        print(card)
        data = {'code': '1', 'message': 'Your card added successfully', 'data': card.data}
        return Response(data)
        # return Response({'code': 1, 'message': 'Your password change successfully', 'data': data},
        # status=status.HTTP_200_OK)


class CardViewSet(viewsets.ModelViewSet):
    # model = Card
    # queryset = model.objects.filter(id=request.user.id)
    serializer_class = CardSerializer
    http_method_names = ['get', 'post', 'delete']
    permission_classes = [IsAuthenticated, IsOwner]
    authentication_classes = [TokenAuthentication]

    def destroy(self, request, *args, **kwargs):
        self.authentication_classes = [TokenAuthentication]
        card = self.get_object()
        card.is_active = 0
        card.save()
        data = {"code": "1", "message": "Card deleted successfully"}
        return Response(data)

    def get_queryset(self):
        return Card.objects.filter(user=self.request.user)

# @action(detail=False, methods=['list'], serializer_class=CardSerializer,
#         permission_classes=[IsAuthenticated])
# def get_card(self, request, *args, **kwargs):
#     """
#     API for change password of user.
#     :param request:
#     :param args:
#     :param kwargs:
#     :return:
#     """
#     card = Card.objects.get(user=request.user)
#     card = CardSerializer(card, many=True)
#     print(card.data)
#     data = {'code': '1', 'message': 'Your card added successfully', 'data': card.data}
#     return Response(data)
#     # return Response({'code': 1, 'message': 'Your password change successfully', 'data': data},
#     # status=status.HTTP_200_OK)
#
# @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
# def remove_card(self, request, *args, **kwargs):
#     """
#     API for removing card of user.
#     :param request:
#     :param args:
#     :param kwargs:
#     :return:
#     """
#     card_id = request.data['card_id']
#     card = Card.objects.get(user=request.user, id=card_id)
#     if card:
#         card.is_active = 0
#         card.save()
#     print(card.is_active)
#     data = {'code': '1', 'message': 'Your card removed successfully'}
#     return Response(data)
#     # return Response({'code': 1, 'message': 'Your password change successfully', 'data': data},
#     # status=status.HTTP_200_OK)

# change password
# https://medium.com/django-rest/django-rest-framework-change-password-and-update-profile-1db0c144c0a3
# https://django-rest-registration.readthedocs.io/en/latest/_modules/rest_registration/api/views/change_password.html#change_password

# reset password
# https://studygyaan.com/django/django-rest-framework-tutorial-change-password-and-reset-password
