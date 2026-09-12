import jwt
from django.contrib.auth import authenticate
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from ninja import Router

from api.schemas.auth_schemas import TokenRequestSchemaIn, TokenRequestSchemaOut, RefreshTokenRequestSchemaIn
from api.schemas.common_schemas import ErrorSchemaOut
from core.models import AuthTokenModel, DogUserModel
from common.auth.jwt_auth import create_jwt

router = Router()


@router.post(
    "/token/refresh/",
    response={200: TokenRequestSchemaOut, 401: ErrorSchemaOut},
    auth=None,
)
def refresh_token(request, credentials: RefreshTokenRequestSchemaIn):
    """Refresh an access token using a refresh token"""
    try:
        refresh_token = AuthTokenModel.objects.get(key=credentials.refresh_token, token_type=AuthTokenModel.TOKEN_TYPE_REFRESH)
    except AuthTokenModel.DoesNotExist:
        return 401, {"error": "Invalid refresh token"}

    if not refresh_token.is_valid():
        return 401, {"error": "Expired refresh token"}
    
    user = refresh_token.user

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
    return 200, {
        "access_token": access_token.key,
        "refresh_token": refresh_token.key,
        "expires_in": expires_in,
    }

@router.post(
    "/token/",
    response={200: TokenRequestSchemaOut, 401: ErrorSchemaOut},
    auth=None,
)
def get_token(request, credentials: TokenRequestSchemaIn):
    """Authenticate a refresh token and return new authentication tokens"""
    user = authenticate(
        username=credentials.username,
        password=credentials.password,
    )
    if user is None:
        return 401, {"error": "Invalid credentials"}

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
    return 200, {
        "access_token": access_token.key,
        "refresh_token": refresh_token.key,
        "expires_in": expires_in,
    }

@router.post(
    "/jwt-token/",
    response={200: TokenRequestSchemaOut, 401: ErrorSchemaOut},
    auth=None
)
def get_jwt_token(request, credentials: TokenRequestSchemaIn):
    """ generate a jwt token for a user"""
    user = authenticate(
        username=credentials.username,
        password=credentials.password,
    )
    if user is None:
        return 401, {"error": "Invalid credentials"}
    
    with transaction.atomic():
        access_token = create_jwt(user.id, token_type='access')
        refresh_token = create_jwt(user.id, token_type='refresh')
    
    return 200, {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "expires_in": 4 * 60 * 60
    }

@router.post(
    "/jwt-token/refresh/",
    response={200: TokenRequestSchemaOut, 401: ErrorSchemaOut},
    auth=None
)
def refresh_jwt_token(request, refresh: RefreshTokenRequestSchemaIn):
    try:
        payload = jwt.decode(
            refresh.refresh_token,
            settings.JWT_SECRET,
            algorithms=["HS256"],
        )
    except jwt.ExpiredSignatureError:
        return 401, {"error": "Expired refresh token"}
    except jwt.DecodeError:
        return 401, {"error": "Invalid refresh token"}

    if payload.get("token_type") != "refresh":
        return 401, {"error": "Invalid refresh token"}

    try:
        user = DogUserModel.objects.get(id=payload.get("user_id"))
    except (DogUserModel.DoesNotExist, ValueError, TypeError):
        return 401, {"error": "Invalid refresh token"}

    access_token = create_jwt(user.id, token_type="access")
    refresh_token = create_jwt(user.id, token_type="refresh")

    return 200, {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "expires_in": 4 * 60 * 60,
    }
