from uuid import UUID

from ninja import Router

from api.logic.bark_logic import (
    handle_barks_list,
    handle_create_bark,
    handle_delete_bark,
    handle_get_bark,
    handle_update_bark,
)
from api.schemas.bark_schemas import (
    BarkCreateUpdateSchemaIn,
    BarkSchemaOut,
)
from api.logic.exceptions import get_error_response
from api.schemas.common_schemas import ErrorSchemaOut
from common.pagination import SkipPagination
from core.models import BarkModel, DogUserModel
from ninja.pagination import paginate

router = Router()

@router.get("/", response=list[BarkSchemaOut], auth=None)
@paginate
def barks_list(request):
    """
    Bark list endpoint that returns a list of barks.
    """
    return handle_barks_list()


@router.post("/", response={201: BarkSchemaOut})
def create_bark(request, bark: BarkCreateUpdateSchemaIn):
    """Create a new bark."""
    return handle_create_bark(request.auth, bark.model_dump())

@router.get("/{bark_id}/", response={200: BarkSchemaOut, 404: ErrorSchemaOut}, auth=None)
def get_bark(request, bark_id: UUID):
    """
    Bark detail endpoint that returns a single bark.
    """
    try:
        return handle_get_bark(bark_id)
    except Exception as exc:
        return get_error_response(exc)

@router.put("/{bark_id}/", response={200: BarkSchemaOut, 404: ErrorSchemaOut})
def update_bark(request, bark_id: UUID, bark: BarkCreateUpdateSchemaIn):
    """Update an existing bark."""
    try:
        return handle_update_bark(bark_id, request.auth, bark.model_dump())
    except Exception as exc:
        return get_error_response(exc)

@router.delete("/{bark_id}/", response={204: None, 404: ErrorSchemaOut})
def delete_bark(request, bark_id: UUID):
    """Delete an existing bark."""

    try:
        handle_delete_bark(bark_id, request.auth)
        return 204, None
    except Exception as exc:
        return get_error_response(exc)
