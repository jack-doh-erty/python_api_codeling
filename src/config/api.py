from django.conf import settings
from ninja import NinjaAPI
from ninja.throttling import AnonRateThrottle

from api.endpoints.auth import router as auth_router
from api.endpoints.barks import router as barks_router
from api.endpoints.sniffs import router as sniffs_router
from api.endpoints.users import router as users_router
from api_v2.endpoints.auth import router as auth_router_v2
from api_v2.endpoints.barks import router as barks_router_v2
from api_v2.endpoints.sniffs import router as sniffs_router_v2
from api_v2.endpoints.users import router as users_router_v2
from common.auth.jwt_auth import JWTAuth
from common.auth.token import TokenAuth

throttle_config = (
    [] if getattr(settings, "TESTING", False) else [AnonRateThrottle("10/m")]
)

api = NinjaAPI(
    auth=[TokenAuth(), JWTAuth()],
    title="Social Dog API",
    version="1.0.0",
    throttle=throttle_config,
)
api_v2 = NinjaAPI(
    auth=[TokenAuth(), JWTAuth()],
    title="Social Dog API v2",
    version="2.0.0",
    throttle=throttle_config,
)

api.add_router("/auth", auth_router, tags=["auth"])
api.add_router("/users", users_router, tags=["users"])
api.add_router("/barks", barks_router, tags=["barks"])
api.add_router("/sniffs", sniffs_router, tags=["sniffs"])

api_v2.add_router("/auth", auth_router_v2, tags=["auth"])
api_v2.add_router("/users", users_router_v2, tags=["users"])
api_v2.add_router("/barks", barks_router_v2, tags=["barks"])
api_v2.add_router("/sniffs", sniffs_router_v2, tags=["sniffs"])
