from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from taxi.utils import GenerateOtp

from taxi.models import User, Driver


class RegisterSerializer(serializers.ModelSerializer):
    """
    A RegisterSerializer is for API of user registartion.
    """
    # error_messages={'required': 'Email field is required1.',
    #                                                    'blank': 'Email field must not be blank1.'
    #                                                    }
    user_type = serializers.IntegerField(error_messages={'required': 'user type field is required1.',
                                                         'blank': 'user type field must not be blank1.'
                                                         })
    email = serializers.EmailField(max_length=128,
                                   error_messages={'required': 'email field is required2.',
                                                   'blank': 'email field must not be blank2.'
                                                   })
    fullname = serializers.CharField(max_length=128,
                                     error_messages={'required': 'fullname field is required3.',
                                                     'blank': 'fullname field must not be blank3.'
                                                     })
    password = serializers.CharField(write_only=True, error_messages={'required': 'password field is required4.',
                                                                      'blank': 'password field must not be blank4.'
                                                                      })
    phone = serializers.CharField(error_messages={'required': 'fullname field is required5.',
                                                  'blank': 'fullname field must not be blank6.'
                                                  })
    licence = serializers.CharField(required=False)
    type_vehicle = serializers.IntegerField(required=False)
    capacity = serializers.IntegerField(required=False)
    rc_book = serializers.CharField(required=False)
    fittness_certificate = serializers.CharField(required=False)
    insurance = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = ['user_type', 'email', 'fullname', 'password', 'profile_image', 'phone', 'licence',
                  'type_vehicle', 'capacity', 'rc_book', 'fittness_certificate', 'insurance']
        extra_kwargs = {
            'profile_image': {'required': False}}

    def validate(self, attrs):
        """
        This method will validate sign up credentials.
        :param attrs:
        :return:
        """
        user_type = attrs.get('user_type')
        licence = attrs.get('licence')
        type_vehicle = attrs.get('type_vehicle')
        capacity = attrs.get('capacity')
        rc_book = attrs.get('rc_book')
        fittness_certificate = attrs.get('fittness_certificate')
        insurance = attrs.get('insurance')

        if user_type == 2:
            if not licence:
                raise AuthenticationFailed({'Licence': 'Driving licence must required, try again!!!'})
            elif not type_vehicle:
                raise AuthenticationFailed('Type Vehicle must required, try again!!!')
            elif not capacity:
                raise AuthenticationFailed('Capacity must required, try again!!!')
            elif not rc_book:
                raise AuthenticationFailed('RC  must required, try again!!!')
            elif not fittness_certificate:
                raise AuthenticationFailed('Fittness Certificate must required, try again!!!')
            elif not insurance:
                raise AuthenticationFailed('insurance must required, try again!!!')

        # if not profile_image:
        #     attrs['profile_image'] = 'profile_image/default.png'

        return super().validate(attrs)

    def create(self, validated_data):
        # print(validated_data)
        # poping driver details if user_type is 2
        licence = validated_data.pop('licence', None)
        type_vehicle = validated_data.pop('type_vehicle', None)
        capacity = validated_data.pop('capacity', None)
        rc_book = validated_data.pop('rc_book', None)
        fittness_certificate = validated_data.pop('fittness_certificate', None)
        insurance = validated_data.pop('insurance', None)

        user = super().create(validated_data)
        user.otp = GenerateOtp.generateOTP()
        user.set_password(validated_data['password'])
        user.save()

        if user.user_type == 2:
            driver = Driver(user=user, licence=licence, type_vehicle=type_vehicle, capacity=capacity, rc_book=rc_book,
                            fittness_certificate=fittness_certificate, insurance=insurance)
            driver.save()
        return user
