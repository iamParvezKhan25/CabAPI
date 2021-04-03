from django.contrib.auth import password_validation, authenticate
from django.contrib.auth.password_validation import validate_password
from django.shortcuts import get_object_or_404
from taxi.utils import GenerateOtp, Util

from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed

from taxi.models import User


__all__ = ['LoginSerializer', 'ChangePasswordSerializer', 'ResetPasswordSerializer', 'OtpSerializer',
           'UserProfileSerialization', 'UpdateUserSerializer', 'ResendOtpSerializer']


class LoginSerializer(serializers.ModelSerializer):
    """
    A LoginSerializers is for API of login user authentication, verified by email.
    """
    email = serializers.EmailField(max_length=128,
                                   error_messages={'required': 'Email field is required1.',
                                                   'blank': 'Email field must not be blank1.'
                                                   })
    password = serializers.CharField(error_messages={'required': 'Password field is required2.',
                                                     'blank': 'Password field must not be blank2.'
                                                     })

    class Meta:
        model = User
        fields = ['email', 'password']

    def validate(self, attrs):
        """
        This method will validate login credentials and also check user is active or not.
        :param attrs:
        :return:
        """
        email = attrs.get('email')
        password = attrs.get('password')
        user = authenticate(email=email, password=password)
        attrs['user'] = user
        data = dict()

        if not user:
            data['code'] = '0'
            data['message'] = 'Invalid credentials, try again!!!'
            raise AuthenticationFailed(data)
        elif not user.otp_verified:
            data['code'] = '0'
            data['message'] = 'Your acount need OTP verification....'
            raise AuthenticationFailed(data)
        elif not user.is_active:
            data['code'] = '0'
            data['message'] = 'Acount is disabled, Contact ADMIN....'
            raise AuthenticationFailed(data)

        return super().validate(attrs)


class OtpSerializer(serializers.ModelSerializer):
    """
    A OtpSerializer is for API of otp verified by user.
    """
    otp = serializers.IntegerField(error_messages={'required': 'user type field is required1.',
                                                   'blank': 'OTP must not empty....'
                                                   })

    class Meta:
        model = User
        fields = ['otp']

    def validate(self, attrs):
        """
        This method will validate login credentials and also check user is active or not.
        :param attrs:
        :return:
        """
        otp = attrs.get('otp')
        # this will provide user id from header(self.context['request'].META.get('HTTP_ID'))
        user = User.objects.get(id=int(self.context['request'].META.get('HTTP_ID')))

        if not user:
            raise AuthenticationFailed('Invalid user, try again!!!')
        elif not user.otp == otp:
            raise AuthenticationFailed('OTP is not valid')
        attrs['user'] = user.id

        return super().validate(attrs)

    def save(self, **kwargs):
        """
        Here we will save new password after all validations of user model.
        :param kwargs:
        :return:
        """
        user = User.objects.get(id=self.validated_data['user'])
        user.otp_verified = 1
        user.otp = 0
        user.save()
        return user


class ResendOtpSerializer(serializers.ModelSerializer):
    """
    A OtpSerializer is for API of otp verified by user.
    """

    class Meta:
        model = User
        fields = ['user_id']

    def validate(self, attrs):
        """
        This method will validate login credentials and also check user is active or not.
        :param attrs:
        :return:
        """
        user_id = int(self.context['request'].META.get('HTTP_ID'))
        user = User.objects.get(id=user_id)
        attrs['user'] = user

        if not user:
            data['code'] = '0'
            data['message'] = 'Invalid user, try again!!!'
            raise AuthenticationFailed(data)

        return super().validate(attrs)

    def save(self, **kwargs):
        """
        Here we will save new password after all validations of user model.
        :param kwargs:
        :return:
        """
        user = User.objects.get(id=self.validated_data['user_id'])
        user_otp = GenerateOtp.generateOTP()
        user.otp = user_otp
        user.save()
        return user


class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['fullname', 'email', 'profile_image']
        extra_kwargs = {'username': {'required': False}, 'email': {'required': False}}


class ChangePasswordSerializer(serializers.ModelSerializer):
    """
    This ChangePasswordSerializer will work for change old password.
    """
    old_password = serializers.CharField(
        max_length=128,
        write_only=True,
        required=True
    )
    new_password = serializers.CharField(
        max_length=128,
        write_only=True,
        required=True,
        validators=[validate_password]
    )
    confirm_password = serializers.CharField(
        max_length=128,
        write_only=True,
        required=True
    )

    class Meta:
        model = User
        fields = ['old_password', 'new_password', 'confirm_password']

    def validate(self, data):
        """
        This method will validate all input data.
        :param data:
        :return:
        """
        if data['new_password'] != data['confirm_password']:
            data['code'] = '0'
            data['message'] = 'New password and confirm password didn\'t matched.'
            raise serializers.ValidationError(data)
        password_validation.validate_password(data['new_password'], self.context['request'].user)
        return data

    def validate_old_password(self, old_password):
        """
        In this method we will validate is old password is matched with stored old password of user model.
        :param old_password:
        :return:
        """
        data = dict()
        user = self.context['request'].user
        if not user.check_password(old_password):
            data['code'] = '0'
            data['message'] = 'Your old password is not correct.'
            raise serializers.ValidationError(data)
        return old_password

    def save(self, **kwargs):
        """
        Here we will save new password after all validations of user model.
        :param kwargs:
        :return:
        """
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class ResetPasswordSerializer(serializers.ModelSerializer):
    """
    Reset Password Serializer will work for resetting password.
    """
    email = serializers.EmailField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['email', ]

    def validate(self, data):
        email = data['email']
        user = User.objects.filter(email=email)

        if not email:
            data['code'] = '0'
            data['message'] = 'Email is empty.'
            raise serializers.ValidationError(data)
        elif not user:
            data['code'] = '0'
            data['message'] = 'Please enter valid email address.'
            raise serializers.ValidationError(data)

        return data

    def save(self, **kwargs):
        """
        Here we will set password based on user email.
        :param kwargs: we get valid email.
        :return:
        """
        email = self.validated_data['email']
        user = get_object_or_404(User, email=email)
        password = User.objects.make_random_password(length=6)
        print('Password => ' + password)
        user.set_password(password)
        user.save()

        # email_body = f'Hi {user.username} this mail is system generated for forget fpassword. \nBecuase you just ' \
        #              f'request for reset password in app name MY ACCOUNT. \nUse this given password for further login '\
        #              f'\"{password}\". '
        #
        # data = {'email_body': email_body, 'to_email': user.email,
        #         'email_subject': f'Welcome, {user.first_name} to MY Account APP.'}
        # Util.send_email(data)

        return user


class UserProfileSerialization(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ['password', 'last_login', 'is_superuser', 'is_staff', 'is_active', 'date_joined', 'otp',
                   'otp_verified', 'update_date', 'id', 'groups', 'user_permissions']
        read_only_fields = ['email']
