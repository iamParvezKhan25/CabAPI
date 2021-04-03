from rest_framework import serializers
from taxi.serializers.user_serializer import UserSeriailzer
from vincenty import vincenty

from taxi.models import Book
from taxi.models import User, Driver


class DriverSerialzer(serializers.ModelSerializer):
    user = UserSeriailzer(read_only=True)

    class Meta:
        model = Driver  # read_only=True
        fields = ['address', 'user']


class BookingSerializer(serializers.ModelSerializer):
    driver = DriverSerialzer(read_only=True)
    driver_id = serializers.IntegerField(write_only=True, error_messages={'required': 'Driver field is required.',
                                                                          'blank': 'Driver field must not be blank.'
                                                                          })

    class Meta:
        model = Book
        fields = ['booking_type', 'pick_up_lat', 'pick_up_lon', 'drop_lat', 'drop_lon', 'capacity', 'shipment_type',
                  'document', 'material_type', 'payment_type', 'card_pay_id', 'driver_id', 'driver']
        extra_kwargs = {
            'payment_type': {'write_only': True},
            'capacity': {'required': False},
            'shipment_type': {'required': False},
            'document': {'required': False, 'write_only': True},
            'material_type': {'required': False},
            'card_pay_id': {'required': False, 'write_only': True},
        }

    def validate(self, attrs):
        """
        This method will validate login credentials and also check user is active or not.
        :param attrs:
        :return:
        """
        booking_type = attrs.get('booking_type')
        capacity = attrs.get('capacity')
        shipment_type = attrs.get('shipment_type')
        document = attrs.get('document')
        material_type = attrs.get('material_type')
        payment_type = attrs.get('payment_type')
        card_pay_id = attrs.get('card_pay_id')
        driver_id = attrs.get('driver_id')
        user = User.objects.get(id=self.context['request'].user.id)

        if booking_type in (1, 2):
            if booking_type == 1:
                if not capacity:
                    serializers.ValidationError({'capacity': 'Capacity must not empty.'})
                if shipment_type not in (1, 2):
                    serializers.ValidationError({'shipment_type': 'Shipment Type is not valid.'})
                elif shipment_type == 2:
                    if not document:
                        serializers.ValidationError({'document': 'Document must required.'})
            else:
                if material_type not in (1, 2):
                    serializers.ValidationError({'material_type': 'Material Type is not valid.'})
        else:
            serializers.ValidationError({'booking_type': 'Booking Type is not valid.'})

        if payment_type in (1, 2, 3):
            if payment_type == 1:
                if not card_pay_id:
                    serializers.ValidationError({'card_pay_id': 'Card ID must not empty.'})
            if payment_type == 3:
                if user.wallet == 0.0:
                    serializers.ValidationError({'wallet': 'Wallet is empty.'})
        else:
            serializers.ValidationError({'payment_type': 'Payment Type is not valid.'})

        pickup = (float(attrs.get('pick_up_lat')), float(attrs.get('pick_up_lon')))
        drop = (float(attrs.get('drop_lat')), float(attrs.get('drop_lon')))

        dist = vincenty(pickup, drop)
        total_amount = dist * 40
        attrs['distance'] = dist
        attrs['total_amount'] = total_amount
        attrs['user'] = user

        return super().validate(attrs)

    def create(self, validated_data):
        driver_id = validated_data.pop('driver_id')
        validated_data['driver'] = Driver.objects.get(id=driver_id)
        book = super().create(validated_data)
        book.save()
        return book
