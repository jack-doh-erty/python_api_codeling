from core.models import BarkModel, DogUserModel
from api.logic.exceptions import DuplicateResourceError, ResourceNotFoundError


def handle_barks_list(favorite_toy=None):
    """Return all barks with their users loaded."""
    if favorite_toy:
        return BarkModel.objects.select_related("user").filter(favorite_toy=favorite_toy).all()
    return BarkModel.objects.select_related("user").all()


def handle_create_bark(user: DogUserModel, data: dict) -> BarkModel:
    data["user_id"] = user.id
    return BarkModel.objects.create(**data)

def handle_get_bark(bark_id: str) -> BarkModel:
    try:
        return BarkModel.objects.select_related("user").get(id=bark_id)
    except BarkModel.DoesNotExist as exc:
        raise ResourceNotFoundError("Bark not found") from exc

def handle_delete_bark(bark_id: str, user: DogUserModel) -> None:
    try:
        obj = BarkModel.objects.filter(user_id=user.id).get(id=bark_id)
    except BarkModel.DoesNotExist as exc:
        raise ResourceNotFoundError("Bark not found") from exc 

    obj.delete()
    return None


def handle_update_bark(
    bark_id: str, user: DogUserModel, data: dict
) -> BarkModel:
    try:
        bark = BarkModel.objects.filter(user_id=user.id).select_related("user").get(
            id=bark_id
        )
    except BarkModel.DoesNotExist as exc:
        raise ResourceNotFoundError("Bark not found") from exc

    for field, value in data.items():
        setattr(bark, field, value)

    bark.save()
    return bark
