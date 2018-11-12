import re

from django.contrib.auth import authenticate

from rest_framework import serializers

from .models import User

from django.core.mail import send_mail

from django.contrib.auth.tokens import default_token_generator

import jwt

from authors.settings import SECRET_KEY


class RegistrationSerializer(serializers.ModelSerializer):
    """Serializers registration requests and creates a new user."""

    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True
    )

    # The client should not be able to send a token along with a registration
    # request. Making `token` read-only handles that for us.

    class Meta:
        model = User
        # List all of the fields that could possibly be included in a request
        # or response, including fields specified explicitly above.
        fields = ['email', 'password', 'username', 'token']
        extra_kwargs = {'username': {
            'write_only': True
        },
            'email': {
                'write_only': True
            }
        }

    def create(self, validated_data):
        
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255, write_only=True)
    password = serializers.CharField(max_length=128, write_only=True)
    token = serializers.CharField(max_length=255, read_only=True)

    class Meta:
        fields = ('email', 'password', 'token')

    def validate(self, data):
        # The `validate` method is where we make sure that the current
        # instance of `LoginSerializer` has "valid". In the case of logging a
        # user in, this means validating that they've provided an email
        # and password and that this combination matches one of the users in
        # our database.
        email = data.get('email', None)
        password = data.get('password', None)

        # The `authenticate` method is provided by Django and handles checking
        # for a user that matches this email/password combination. Notice how
        # we pass `email` as the `username` value. Remember that, in our User
        # model, we set `USERNAME_FIELD` as `email`.
        user = authenticate(username=email, password=password)

        # If no user was found matching this email/password combination then
        # `authenticate` will return `None`. Raise an exception in this case.
        # import pdb; pdb.set_trace()
        if user is None:
            raise serializers.ValidationError(
                'A user with this email and password was not found.'
            )

        # Django provides a flag on our `User` model called `is_active`. The
        # purpose of this flag to tell us whether the user has been banned
        # or otherwise deactivated. This will almost never be the case, but
        # it is worth checking for. Raise an exception in this case.
        if not user.is_active:
            raise serializers.ValidationError(
                'This user has been deactivated.'
            )

        # The `validate` method should return a dictionary of validated data.
        # This is the data that is passed to the `create` and `update` methods
        # that we will see later on.
        return {
            "email": user.email,
            "token": user.token
        }

class CustomUserDetailsSerializer(serializers.ModelSerializer):
    """
    serializer class for django rest auth social login
    """
    email = serializers.CharField(max_length=255)
    username = serializers.CharField(max_length=255)
    token = serializers.CharField(max_length=255, read_only=True)
    class Meta:
        model = User
        fields = ('email','username','token')

class UserSerializer(serializers.ModelSerializer):
    """Handles serialization and deserialization of User objects."""

    # Passwords must be at least 8 characters, but no more than 128
    # characters. These values are the default provided by Django. We could
    # change them, but that would create extra work while introducing no real
    # benefit, so let's just stick with the defaults.
    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True
    )

    class Meta:
        model = User
        fields = ('email', 'username', 'password')

        # The `read_only_fields` option is an alternative for explicitly
        # specifying the field with `read_only=True` like we did for password
        # above. The reason we want to use `read_only_fields` here is because
        # we don't need to specify anything else about the field. For the
        # password field, we needed to specify the `min_length` and
        # `max_length` properties too, but that isn't the case for the token
        # field.

    def update(self, instance, validated_data):
        """Performs an update on a User."""

        # Passwords should not be handled with `setattr`, unlike other fields.
        # This is because Django provides a function that handles hashing and
        # salting passwords, which is important for security. What that means
        # here is that we need to remove the password field from the
        # `validated_data` dictionary before iterating over it.
        password = validated_data.pop('password', None)

        for (key, value) in validated_data.items():
            # For the keys remaining in `validated_data`, we will set them on
            # the current `User` instance one at a time.
            setattr(instance, key, value)

        if password is not None:
            # `.set_password()` is the method mentioned above. It handles all
            # of the security stuff that we shouldn't be concerned with.
            instance.set_password(password)

        # Finally, after everything has been updated, we must explicitly save
        # the model. It's worth pointing out that `.set_password()` does not
        # save the model.
        instance.save()

        return instance


class ResetPasswordSerializer(serializers.Serializer):
    """Serializers resets password."""
    email = serializers.CharField(required=True)
    new_password = serializers.CharField(max_length=128, required=True, min_length=8)
    confirm_password = serializers.CharField(max_length=128, required=True, min_length=8)

    def validate(self, data):
        new_password = data.get('new_password', None)
        confirm_password = data.get('confirm_password', None)
        token = self.context.get('token')
        email = data.get('email', None)
        if new_password != confirm_password:
            raise serializers.ValidationError('Passwords do not match.')
        user = User.objects.get(email=email)
        if not (default_token_generator.check_token(user, token)):
            raise serializers.ValidationError(
                "You either have an invalid token or email")
        user.set_password(new_password)
        user.save()
        return data

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=255, required=True)
    username = serializers.CharField(required=False)
    token = serializers.CharField(required=False)

    def validate(self, data):
        email = data.get('email', None)
        user = User.objects.filter(email=data.get('email', None)).first()
        if user is None:
            raise serializers.ValidationError(
                'No records found with the email address. Create An Account To Continue.'
            )
        else:
            token = default_token_generator.make_token(user)
            username = user.username
            return ({
                "email":email,
                "username":username,
                "token":token
            })
