from ninja import Router

from api.logic.exceptions import get_error_response
from api.logic.sniff_logic import handle_create_sniff
from api.schemas.common_schemas import ErrorSchemaOut
from api.schemas.sniff_schemas import SniffCreateSchemaIn, SniffSchemaOut

router = Router()


@router.post(
    "/",
    response={201: SniffSchemaOut, 409: ErrorSchemaOut, 404: ErrorSchemaOut},
)
def create_sniff(request, sniff: SniffCreateSchemaIn):
    """Sniff a bark."""
    try:
        bark = handle_create_sniff(
            bark_id=sniff.bark_id,
            user=request.auth,
        )
    except Exception as exc:
        return get_error_response(exc)

    return 201, bark
