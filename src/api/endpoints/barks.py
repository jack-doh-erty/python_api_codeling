from uuid import UUID

from ninja import Router

from api.schemas.bark_schemas import BarkSchemaOut, ErrorSchemaOut, BarkSchemaIn
from core.models import BarkModel

router = Router()


@router.get("/", response=list[BarkSchemaOut])
def barks_list(request):
    """
    Bark list endpoint that returns a list of barks.
    """
    return BarkModel.objects.all()

@router.get("/{bark_id}/", response={200: BarkSchemaOut, 404: ErrorSchemaOut})
def get_bark(request, bark_id: UUID):
    """
    Bark detail endpoint that returns a single bark.
    """
    try:
        return BarkModel.objects.get(id=bark_id)
    except BarkModel.DoesNotExist:
        return 404, {"error": "Bark not found"}

@router.put("/{bark_id}/", response={200: BarkSchemaOut, 404: ErrorSchemaOut})
def update_bark(request, bark_id: int, bark: BarkSchemaIn):
    """Update an existing bark."""
    if bark_id in (1, 2, 3):
        return 200, {
            "id": bark_id,
            "message": bark.message
        }
    return 404, {"error": "Bark not found"}

@router.delete("/{bark_id}/", response={204: None, 404: ErrorSchemaOut})
def delete_bark(request, bark_id: int):
    # Your deletion logic here!
    if bark_id in (1, 2, 3):
        return 204, None
    return 404, {"error": "Bark not found"}
