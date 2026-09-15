from ninja import Router

from api_v2.logic.exceptions import get_error_response
from api_v2.logic.sniff_logic import handle_create_sniff
from api_v2.schemas.common_schemas import ErrorSchemaOut
from api_v2.schemas.sniff_schemas import SniffCreateSchemaIn, SniffSchemaOut

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
