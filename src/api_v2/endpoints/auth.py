import jwt
from django.contrib.auth import authenticate
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from ninja import Form, Router

from api_v2.logic.auth_logic import (
    handle_get_jwt_token,
    handle_get_token,
    handle_refresh_jwt_token,
    handle_refresh_token,
)
from api_v2.logic.exceptions import get_error_response
from api_v2.schemas.auth_schemas import TokenRequestSchemaIn, TokenRequestSchemaOut, RefreshTokenRequestSchemaIn
from api_v2.schemas.common_schemas import ErrorSchemaOut
from core.models import AuthTokenModel, DogUserModel
from common.auth.jwt_auth import create_jwt

router = Router()


@router.post(
    "/token/refresh/",
    response={200: TokenRequestSchemaOut, 401: ErrorSchemaOut},
    auth=None,
)
def refresh_token(request, credentials: Form[RefreshTokenRequestSchemaIn]):
    """Refresh an access token using a refresh token"""
    try:
        return handle_refresh_token(credentials.refresh_token)
    except Exception as exc:
        return get_error_response(exc)

@router.post(
    "/token/",
    response={200: TokenRequestSchemaOut, 401: ErrorSchemaOut},
    auth=None,
)
def get_token(request, credentials: Form[TokenRequestSchemaIn]):
    """Authenticate a refresh token and return new authentication tokens"""
    try:
        return handle_get_token(credentials.username, credentials.password)
    except Exception as exc:
        return get_error_response(exc)

@router.post(
    "/jwt-token/",
    response={200: TokenRequestSchemaOut, 401: ErrorSchemaOut},
    auth=None
)
def get_jwt_token(request, credentials: Form[TokenRequestSchemaIn]):
    """ generate a jwt token for a user"""
    try:
        return handle_get_jwt_token(credentials.username, credentials.password)
    except Exception as exc:
        return get_error_response(exc)

@router.post(
    "/jwt-token/refresh/",
    response={200: TokenRequestSchemaOut, 401: ErrorSchemaOut},
    auth=None
)
def refresh_jwt_token(request, refresh: Form[RefreshTokenRequestSchemaIn]):
    try:
        return handle_refresh_jwt_token(refresh.refresh_token)
    except Exception as exc:
        return get_error_response(exc)
