from core.models import BarkModel, UserSniffModel
from api_v2.logic.exceptions import ResourceNotFoundError, DuplicateResourceError


def handle_create_sniff(bark_id: str, user) -> BarkModel:
    """Handle creating a sniff (like) on a bark"""
    # 1: get bark_id from DB. Raise ResourceNotFoundError("Bark not found") if not found.
    try:
        bark = BarkModel.objects.get(id=bark_id)
    except BarkModel.DoesNotExist as exc:
        raise ResourceNotFoundError("Bark not found") from exc

    # 2: Check if user has already sniffed this bark. Raise DuplicateResourceError("You've already sniffed this bark") if they have.
    if UserSniffModel.objects.filter(user=user, bark=bark).exists():
        raise DuplicateResourceError("You've already sniffed this bark")

    # 3: Create the new sniff for the bark + user
    UserSniffModel.objects.create(user=user, bark=bark)

    # 4: Increment the sniff_count for the bark
    bark.sniff_count += 1
    bark.save()

    # 5: Return the bark
    return bark
