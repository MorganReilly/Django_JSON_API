from rest_framework import serializers

from django.contrib.auth import authenticate

from conduit.apps.profiles.serializers import ProfileSerializer

from .models import User


class RegistrationSerializer(serializers.ModelSerializer):
    """
    Serializers registration requests and creates a new user.
    """

    # Ensure passwords are at least 8 characters long, no longer than 128
    # characters, and cannot be read by the client
    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True
    )

    # The client should not be able to send a token along with a registration
    # request. Making 'token' read-only handles that for us.
    token = serializers.CharField(max_length=255, read_only=True)

    class Meta:
        model = User
        # List all of the fields that could possibly be included in a request
        # or response, including fields specified explicitly above
        fields = ['email', 'username', 'password', 'token']

    def create(self, validated_data):
        # Using 'create_user' method to create new user
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=255)
    username = serializers.CharField(max_length=255, read_only=True)
    password = serializers.CharField(max_length=128, write_only=True)
    token = serializers.CharField(max_length=255, read_only=True)

    def validate(self, data):
        # This method is where we make sure that the current instance of
        # 'LoginSerializer' has "valid". In the case of logging a user in,
        # this means validating that they've provided an email and
        # password and that this combination matches one of the users in db
        email = data.get('email', None)
        password = data.get('password', None)

        # Raise exception if email not provided
        if email is None:
            raise serializers.ValidationError(
                'Email required to log in'
            )

        # Raise exception if password not provided
        if password is None:
            raise serializers.ValidationError(
                'Password required to log in'
            )

        # 'authenticate' method is provided by Django and handles checking
        # for a user that matches this email/password combination.
        user = authenticate(username=email, password=password)

        # Raise exception if no user found matching email/password
        if user is None:
            raise serializers.ValidationError(
                'email/password not found'
            )

        # Check if user banned or deactivated
        if not user.is_active:
            raise serializers.ValidationError(
                'User has been deactivated'
            )

        # Return dictionary of validated data
        return {
            'email': user.email,
            'username': user.username,
            'token': user.token
        }


class UserSerializer(serializers.ModelSerializer):
    """
    Handles serialization and deserialization of User objects.
    """

    # Passwords must have at >= 8 character, <= 128
    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True
    )

    profile = ProfileSerializer(write_only=True)

    bio = serializers.CharField(source='profile.bio', read_only=True)
    image = serializers.CharField(source='profile.image', read_only=True)

    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'token', 'profile', 'bio', 'image',)

        # 'read_only_fields' option is alternative for explicitly specifying
        # field with 'read_only=True', like with password above
        read_only_fields = ('token',)

    def update(self, instance, validated_data):
        """
        Performs an update on a User.
        """
        password = validated_data.pop('password', None)

        profile_data = validated_data.pop('profile', {})

        for (key, value) in validated_data.items():
            # For keys remaining in 'validated_data', set them
            # on current 'User' instance one at a time
            setattr(instance, key, value)

        if password is not None:
            # '.set_password()' handles all of the
            # security stuff that we shouldn't be concered with
            instance.set_password(password)

        # Save model
        instance.save()

        for (key, value) in profile_data.items():
            setattr(instance.profile, key, value)

        instance.profile.save()

        return instance
