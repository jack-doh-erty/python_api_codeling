from ninja import Router
from uuid import UUID

from api.schemas.common_schemas import ErrorSchemaOut
from api.schemas.user_schemas import (
    DogUserCreateSchemaIn,
    DogUserSchemaOut,
    DogUserUpdateSchemaIn,
    DogUserWithTokenSchemaOut,
)
from core.models import AuthTokenModel, DogUserModel

router = Router()


@router.get("/", response=list[DogUserSchemaOut])
def dog_users_list(request):
    """Return a list of dog users."""
    return DogUserModel.objects.all()


@router.get("/me/", response={200: DogUserSchemaOut})
def get_current_user(request):
    """
    Endpoint that returns the currently authenticated user.
    """
    return 200, request.auth


@router.get("/{user_id}/", response={200: DogUserSchemaOut, 404: ErrorSchemaOut})
def get_bark(request, user_id: UUID):
    """
    User detail endpoint that returns a single user.
    """
    try:
        return DogUserModel.objects.get(id=user_id)
    except DogUserModel.DoesNotExist:
        return 404, {"error": "Dog user not found"}


@router.post("/", response={201: DogUserWithTokenSchemaOut, 400: ErrorSchemaOut}, auth=None)
def create_dog_user(request, user: DogUserCreateSchemaIn):
    """Create a new dog user."""
    if DogUserModel.objects.filter(username=user.username).exists():
        return 400, {"error": "Username already exists"}

    new_user_object = DogUserModel.objects.create_user(
        username=user.username,
        password=user.password,
    )
    token = AuthTokenModel.objects.create(user=new_user_object)
    return 201, {"user": new_user_object, "token": token.key}


@router.patch("/me/", response={200: DogUserSchemaOut, 400: ErrorSchemaOut})
def update_me(request, user: DogUserUpdateSchemaIn):
    """Update fields provided for the currently authenticated user."""
    obj = request.auth

    if user.username and DogUserModel.objects.filter(username=user.username).exclude(id=obj.id).exists():
        return 400, {"error": "Username already exists"}

    for field, value in user.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    obj.save()
    return 200, obj
