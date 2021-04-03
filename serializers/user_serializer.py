from rest_framework import serializers

from taxi.models import User


class UserSeriailzer(serializers.ModelSerializer):
    # id = serializers.CharField()

    class Meta:
        model = User
        fields = ['id', 'fullname', 'email', 'profile_image']
