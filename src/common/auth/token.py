from ninja.security import HttpBearer

from core.models import AuthTokenModel


class TokenAuth(HttpBearer):
    def authenticate(self, request, token):
        """Authenticate a request using a token.

        Args:
            request: The HTTP request
            token: The token string from the Authorization header

        Returns:
            The user if authentication successful, None otherwise
        """
        try:
            token_obj = AuthTokenModel.objects.get(key=token, token_type=AuthTokenModel.TOKEN_TYPE_ACCESS)
        except AuthTokenModel.DoesNotExist:
            return None

        if not token_obj.is_valid():
            return None

        return token_obj.user
