from uuid import UUID

from ninja import Router

from api.schemas.bark_schemas import (
    BarkCreateUpdateSchemaIn,
    BarkSchemaOut,
)
from api.schemas.common_schemas import ErrorSchemaOut
from core.models import BarkModel, DogUserModel

router = Router()


@router.get("/", response=list[BarkSchemaOut], auth=None)
def barks_list(request):
    """
    Bark list endpoint that returns a list of barks.
    """
    return BarkModel.objects.select_related("user").all()


@router.post("/", response={201: BarkSchemaOut})
def create_bark(request, bark: BarkCreateUpdateSchemaIn):
    """Create a new bark."""
    data = bark.dict()
    data["user_id"] = request.auth.id
    obj = BarkModel.objects.create(**data)
    return 201, obj

@router.get("/{bark_id}/", response={200: BarkSchemaOut, 404: ErrorSchemaOut}, auth=None)
def get_bark(request, bark_id: UUID):
    """
    Bark detail endpoint that returns a single bark.
    """
    try:
        return BarkModel.objects.select_related("user").get(id=bark_id)
    except BarkModel.DoesNotExist:
        return 404, {"error": "Bark not found"}

@router.put("/{bark_id}/", response={200: BarkSchemaOut, 404: ErrorSchemaOut})
def update_bark(request, bark_id: UUID, bark: BarkCreateUpdateSchemaIn):
    """Update an existing bark."""
    try:
        obj = BarkModel.objects.filter(user_id=request.auth.id).select_related("user").get(id=bark_id)
    except BarkModel.DoesNotExist:
        return 404, {"error": "Bark not found"}

    for field, value in bark.dict().items():
        setattr(obj, field, value)
    obj.save()
    return 200, obj

@router.delete("/{bark_id}/", response={204: None, 404: ErrorSchemaOut})
def delete_bark(request, bark_id: UUID):
    """Delete an existing bark."""
    try:
        obj = BarkModel.objects.filter(user_id=request.auth.id).get(id=bark_id)
    except BarkModel.DoesNotExist:
        return 404, {"error": "Bark not found"}

    obj.delete()
    return 204, None
