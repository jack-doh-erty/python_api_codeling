from django.core.files.storage import default_storage
from django.db.models import QuerySet
from ninja.files import UploadedFile

from common.filters import UsersFilter, apply_ordering
from core.models import AuthTokenModel, DogUserModel
from api_v2.logic.exceptions import (
    DuplicateResourceError,
    InvalidFileError,
    ResourceNotFoundError,
)


def handle_dog_users_list(filters: UsersFilter) -> QuerySet[DogUserModel]:
    """
    Handle the logic for listing dog users.
    """
    objs = DogUserModel.objects.all()
    return apply_ordering(filters.filter(objs), filters.order_by)


def handle_get_dog_user(user_id: int) -> DogUserModel:
    """Return a dog user by ID, raising a logic error when not found."""
    try:
        return DogUserModel.objects.get(id=user_id)
    except DogUserModel.DoesNotExist as exc:
        raise ResourceNotFoundError("Dog user not found") from exc


def handle_get_current_user(user: DogUserModel) -> DogUserModel:
    """Return the currently authenticated dog user."""
    return user


def handle_create_dog_user(
    username: str, password: str
) -> tuple[DogUserModel, AuthTokenModel]:
    """Create a dog user and their authentication token."""
    if DogUserModel.objects.filter(username=username).exists():
        raise DuplicateResourceError("Username already exists")

    user = DogUserModel.objects.create_user(
        username=username,
        password=password,
    )
    token = AuthTokenModel.objects.create(user=user)
    return user, token


def handle_update_me(user: DogUserModel, data: dict) -> DogUserModel:
    """Update the authenticated user with the supplied fields."""
    username = data.get("username")
    if (
        username is not None
        and DogUserModel.objects.filter(username=username)
        .exclude(id=user.id)
        .exists()
    ):
        raise DuplicateResourceError("Username already exists")

    for field, value in data.items():
        setattr(user, field, value)

    user.save()
    return user


def handle_upload_profile_image(
    user: DogUserModel, image: UploadedFile
) -> DogUserModel:
    """
    Handle the logic for uploading a profile image.
    Validates the image and saves it to the user's profile.
    """
    allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    if image.content_type not in allowed_types:
        raise InvalidFileError("Invalid image type")

    max_size = 5 * 1024 * 1024
    if image.size > max_size:
        raise InvalidFileError("Image size too large")

    if user.profile_image:
        if default_storage.exists(user.profile_image.name):
            default_storage.delete(user.profile_image.name)

    user.profile_image = image
    user.save()
    return user
