from core.models import AuthTokenModel, DogUserModel
from api.logic.exceptions import DuplicateResourceError, ResourceNotFoundError


def handle_dog_users_list():
    """
    Handle the logic for listing dog users.
    Returns a list of all dog users.
    """
    return DogUserModel.objects.all()


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
