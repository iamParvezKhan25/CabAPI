from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed

from taxi.models import Card

__all__ = ['CardSerializer']


class CardSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=128, error_messages={'required': 'Card Holder Name  field is required.',
                                                                 'blank': 'Card Holer Name field must not be blank.'
                                                                 })
    card_no = serializers.CharField(max_length=16, error_messages={'required': 'Card Number field is required.',
                                                                   'blank': 'Card Number field must not be blank.'
                                                                   })
    expiry_month = serializers.CharField(max_length=2, error_messages={'required': 'Expiry Month field is required.',
                                                                       'blank': 'Expiry Month field must not be blank.'
                                                                       })
    expiry_year = serializers.CharField(max_length=2, error_messages={'required': 'Expiry Year field is required.',
                                                                      'blank': 'Expiry Year field must not be blank.'
                                                                      })
    id = serializers.CharField(read_only=True)

    class Meta:
        model = Card
        fields = ['card_no', 'name', 'expiry_month', 'expiry_year', 'id']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        card = super().create(validated_data)
        # card.user = self.context['request'].user
        card.save()
        return card
