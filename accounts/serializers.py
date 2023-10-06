from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer as JwtTokenObtainPairSerializer


class TokenObtainPairSerializer(JwtTokenObtainPairSerializer):
    contact = serializers.CharField()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('email', 'password', 'first_name', 'last_name', 'phone_number', 'user_type')