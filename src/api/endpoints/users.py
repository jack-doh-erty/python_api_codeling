from ninja import Router
from uuid import UUID

from api.schemas.common_schemas import ErrorSchemaOut
from api.schemas.user_schemas import (
    DogUserCreateSchemaIn,
    DogUserSchemaOut,
    DogUserUpdateSchemaIn,
    DogUserWithTokenSchemaOut,
)
from api.logic.user_logic import (
    handle_create_dog_user,
    handle_dog_users_list,
    handle_get_current_user,
    handle_get_dog_user,
    handle_update_me,
)
from api.logic.exceptions import get_error_response

router = Router()


@router.get("/", response=list[DogUserSchemaOut])
def dog_users_list(request):
    """Return a list of dog users."""
    users = handle_dog_users_list()
    return users


@router.get("/me/", response={200: DogUserSchemaOut})
def get_current_user(request):
    """
    Endpoint that returns the currently authenticated user.
    """
    return handle_get_current_user(user=request.auth)


@router.get(
    "/{user_id}/",
    response={200: DogUserSchemaOut, 404: ErrorSchemaOut, 500: ErrorSchemaOut},
)
def get_dog_user(request, user_id: UUID):
    """
    User detail endpoint that returns a single user.
    """
    try:
        return handle_get_dog_user(user_id=user_id)
    except Exception as exc:
        return get_error_response(exc)


@router.post("/", response={201: DogUserWithTokenSchemaOut, 409: ErrorSchemaOut}, auth=None)
def create_dog_user(request, user: DogUserCreateSchemaIn):
    """Create a new dog user."""
    try:
        new_user_object, token = handle_create_dog_user(
            username=user.username,
            password=user.password,
        )
    except Exception as exc:
        return get_error_response(exc)

    return 201, {"user": new_user_object, "token": token.key}


@router.patch(
    "/me/",
    response={200: DogUserSchemaOut, 409: ErrorSchemaOut, 500: ErrorSchemaOut},
)
def update_me(request, user: DogUserUpdateSchemaIn):
    """Update fields provided for the currently authenticated user."""
    try:
        updated_user = handle_update_me(
            user=request.auth,
            data=user.model_dump(exclude_unset=True),
        )
    except Exception as exc:
        return get_error_response(exc)

    return 200, updated_user
