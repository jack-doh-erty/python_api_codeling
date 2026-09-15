import jwt
from django.conf import settings
from django.contrib.auth import authenticate
from django.db import transaction
from django.utils import timezone

from api_v2.logic.exceptions import (
    AuthenticationError,
    TokenExpiredError,
    TokenInvalidError,
)
from common.auth.jwt_auth import create_jwt
from core.models import AuthTokenModel, DogUserModel


def handle_get_token(username: str, password: str) -> dict:
    user = authenticate(username=username, password=password)
    if user is None:
        raise AuthenticationError("Invalid credentials")

    with transaction.atomic():
        AuthTokenModel.objects.filter(user=user).delete()
        access_token = AuthTokenModel.objects.create(
            user=user,
            token_type=AuthTokenModel.TOKEN_TYPE_ACCESS,
        )
        refresh_token = AuthTokenModel.objects.create(
            user=user,
            token_type=AuthTokenModel.TOKEN_TYPE_REFRESH,
        )

    expires_in = int((access_token.expires - timezone.now()).total_seconds())
    return {
        "access_token": access_token.key,
        "refresh_token": refresh_token.key,
        "expires_in": expires_in,
    }


def handle_refresh_token(refresh_token: str) -> dict:
    try:
        token = AuthTokenModel.objects.select_related("user").get(
            key=refresh_token,
            token_type=AuthTokenModel.TOKEN_TYPE_REFRESH,
        )
    except AuthTokenModel.DoesNotExist as exc:
        raise TokenInvalidError("Invalid refresh token") from exc

    if not token.is_valid():
        raise TokenExpiredError("Expired refresh token")

    user = token.user
    with transaction.atomic():
        AuthTokenModel.objects.filter(user=user).delete()
        access_token = AuthTokenModel.objects.create(
            user=user,
            token_type=AuthTokenModel.TOKEN_TYPE_ACCESS,
        )
        new_refresh_token = AuthTokenModel.objects.create(
            user=user,
            token_type=AuthTokenModel.TOKEN_TYPE_REFRESH,
        )

    expires_in = int((access_token.expires - timezone.now()).total_seconds())
    return {
        "access_token": access_token.key,
        "refresh_token": new_refresh_token.key,
        "expires_in": expires_in,
    }


def handle_get_jwt_token(username: str, password: str) -> dict:
    user = authenticate(username=username, password=password)
    if user is None:
        raise AuthenticationError("Invalid credentials")

    access_token = create_jwt(user.id, token_type="access")
    refresh_token = create_jwt(user.id, token_type="refresh")

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "expires_in": 4 * 60 * 60,
    }


def handle_refresh_jwt_token(refresh_token: str) -> dict:
    try:
        payload = jwt.decode(
            refresh_token,
            settings.JWT_SECRET,
            algorithms=["HS256"],
        )
    except jwt.ExpiredSignatureError as exc:
        raise TokenExpiredError("Expired refresh token") from exc
    except jwt.PyJWTError as exc:
        raise TokenInvalidError("Invalid refresh token") from exc

    if payload.get("token_type") != "refresh":
        raise TokenInvalidError("Invalid refresh token")

    try:
        user = DogUserModel.objects.get(id=payload.get("user_id"))
    except (DogUserModel.DoesNotExist, ValueError, TypeError) as exc:
        raise TokenInvalidError("Invalid refresh token") from exc

    return {
        "access_token": create_jwt(user.id, token_type="access"),
        "refresh_token": create_jwt(user.id, token_type="refresh"),
        "expires_in": 4 * 60 * 60,
    }
