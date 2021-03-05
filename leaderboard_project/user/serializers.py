from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('user_id', 'display_name', 'points', 'rank')

    def create(self, validated_data):
        user = User(
            display_name=validated_data['display_name'],
        )
        user.save()
        return user

    def update(self, instance, validated_data):

        for (key, value) in validated_data.items():
            setattr(instance, key, value)

        instance.save()

        return instance