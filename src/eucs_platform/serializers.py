from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_auth.serializers import UserDetailsSerializer
User = get_user_model()

class UserSerializer(UserDetailsSerializer):
    class Meta:
        model = User
        fields = ['name', 'email', 'password']

