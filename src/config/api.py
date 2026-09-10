from ninja import NinjaAPI
from api.endpoints.barks import router as barks_router

api = NinjaAPI()

api.add_router("/barks", barks_router)
