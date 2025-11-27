from rest_framework import serializers
from dj_rest_auth.registration.serializers import RegisterSerializer as BaseRegisterSerializer
from dj_rest_auth.serializers import LoginSerializer as BaseLoginSerializer
from dj_rest_auth.serializers import JWTSerializer as BaseJWTSerializer
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model with basic profile information.
    """
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'full_name', 'is_active', 'is_staff', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class UserCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new users by admins.
    Requires email, password, first_name, and last_name.
    """
    password = serializers.CharField(write_only=True, required=True, min_length=8)

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'password', 'is_active', 'is_staff']
        read_only_fields = ['id']

    def create(self, validated_data):
        """
        Create a new user with the provided data.
        """
        password = validated_data.pop('password')
        email = validated_data.pop('email')
        user = User.objects.create_user(
            email=email,
            password=password,
            **validated_data
        )
        return user


class LoginSerializer(BaseLoginSerializer):
    """
    Custom login serializer that uses email instead of username.
    """
    username = None  # Remove the default username field
    email = serializers.EmailField(
        label="Email",
        write_only=True,
        required=True,
        help_text="User email address"
    )

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            self.user = authenticate(
                request=self.context.get('request'),
                username=email,  # Authenticate with email as username
                password=password
            )

            if not self.user:
                msg = 'Unable to log in with provided credentials.'
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = 'Must include "email" and "password".'
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = self.user
        return attrs


class RegisterSerializer(BaseRegisterSerializer):
    """
    Custom registration serializer that requires first_name and last_name.
    Handles email-based authentication instead of username.
    """
    first_name = serializers.CharField(required=True, max_length=150)
    last_name = serializers.CharField(required=True, max_length=150)

    def get_cleaned_data(self):
        # Get data from parent class
        data = super().get_cleaned_data()
        data['first_name'] = self.validated_data.get('first_name', '')
        data['last_name'] = self.validated_data.get('last_name', '')
        return data

    def save(self, request):
        # Get the email from parent validation
        cleaned_data = self.get_cleaned_data()

        # Create user with our custom manager
        user = User.objects.create_user(
            email=cleaned_data.get('email'),
            password=cleaned_data.get('password1'),
            first_name=cleaned_data.get('first_name', ''),
            last_name=cleaned_data.get('last_name', ''),
        )
        return user


class JWTSerializer(BaseJWTSerializer):
    """
    Custom JWT serializer to return tokens with expected field names.
    Frontend expects 'access_token' and 'refresh_token' instead of 'access' and 'refresh'.
    """
    def to_representation(self, instance):
        """Override to rename token fields."""
        representation = super().to_representation(instance)

        # Rename fields to match frontend expectations
        if 'access' in representation:
            representation['access_token'] = representation.pop('access')
        if 'refresh' in representation:
            representation['refresh_token'] = representation.pop('refresh')

        return representation
