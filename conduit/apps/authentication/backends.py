import jwt

from django.conf import settings

from rest_framework import authentication, exceptions

from .models import User


class JWTAuthentication(authentication.BaseAuthentication):
    authentication_header_prefix = 'Token'

    def authenticate(self, request):
        """
        'authenticate' method called on every request regardless of whether
        endpoint requires authentication.

        'authenticate' has 2 possible return values:

        1) 'None' - Return this is if do not wish to authenticate.
                    Usually means auth will fail ie. req does not include token in header

        2) '(user, token)' - Return user/token combination when authentication is successful
        """
        request.user = None

        # 'auth_header' an array with two elements:
        # 1: name of auth header -- 'token'
        # 2: JWT (JSON Web Token) to auth against
        auth_header = authentication.get_authorization_header(request).split()
        auth_header_prefix = self.authentication_header_prefix.lower()

        if not auth_header:
            return None

        if len(auth_header) == 1:
            # Invalid token header. No credentials provided. Do not attempt to authenticate
            return None

        elif len(auth_header) > 2:
            # Invalid token header. Token string should not contain spaces. Do not attempt to authenticate
            return None

        # Need to decode 'prefix' and 'token' since JWT library can't handle 'byte' type
        prefix = auth_header[0].decode('utf-8')
        token = auth_header[1].decode('utf-8')

        if prefix.lower() != auth_header_prefix:
            # auth header is not what was expected. Do not attempt to authenticate
            return None

        return self._authenticate_credentials(request, token)

    def _authenticate_credentials(self, request, token):
        """
        Try to authenticate the given credentials. If authentication is
        successful, return the user and token. If not, throw an error.
        """
        try:
            payload = jwt.decode(token, settings.SECRET_KEY)
        except:
            msg = 'Invalid authentication. Could not decode token.'
            raise exceptions.AuthenticationFailed(msg)

        try:
            user = User.objects.get(pk=payload['id'])
        except User.DoesNotExist:
            msg = 'No user matching this token was found.'
            raise exceptions.AuthenticationFailed(msg)

        if not user.is_active:
            msg = 'This user has been deactivated.'
            raise exceptions.AuthenticationFailed(msg)

        return (user, token)
