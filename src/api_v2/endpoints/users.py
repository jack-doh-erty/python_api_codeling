from ninja import File, Query, Router
from ninja.files import UploadedFile
from uuid import UUID

from api_v2.schemas.common_schemas import ErrorSchemaOut
from api_v2.schemas.user_schemas import (
    DogUserCreateSchemaIn,
    DogUserSchemaOut,
    DogUserUpdateSchemaIn,
    DogUserWithTokenSchemaOut,
)
from api_v2.logic.user_logic import (
    handle_create_dog_user,
    handle_dog_users_list,
    handle_get_current_user,
    handle_get_dog_user,
    handle_upload_profile_image,
    handle_update_me,
)
from api_v2.logic.exceptions import get_error_response
from common.filters import UsersFilter
from ninja.pagination import paginate

router = Router()


@router.get("/", response=list[DogUserSchemaOut])
@paginate
def dog_users_list(request, filters: UsersFilter = Query(...)):
    """
    Endpoint that returns a list of dog users.
    """
    users = handle_dog_users_list(filters=filters)
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


@router.post(
    "/me/profile-image/",
    response={200: DogUserSchemaOut, 400: ErrorSchemaOut},
)
def upload_profile_image(request, image: UploadedFile = File(...)):
    """
    Endpoint for uploading a profile image for the current user.
    """
    try:
        updated_user = handle_upload_profile_image(
            user=request.auth,
            image=image,
        )
    except Exception as exc:
        return get_error_response(exc)

    return 200, updated_user
