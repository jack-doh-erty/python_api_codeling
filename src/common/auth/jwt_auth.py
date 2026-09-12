import time
from uuid import UUID

import jwt
from django.conf import settings
from core.models import DogUserModel

from ninja.security import HttpBearer

def create_jwt(user_id: UUID, token_type: str) -> str:
    exp_seconds = {
        "access": 4 * 60 * 60,
        "refresh": 7 * 24 * 60 * 60,
    }[token_type]

    payload = {
        "user_id": str(user_id),
        "token_type": token_type,
        "iat": int(time.time()),
        "exp": int(time.time()) + exp_seconds,
    }

    return jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")

class JWTAuth(HttpBearer):
    def authenticate(self, request, token):
        try:
            token_obj = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        except jwt.PyJWTError:
            return None

        if not token_obj["token_type"] == "access":
            return None

        return DogUserModel.objects.get(id=token_obj["user_id"])