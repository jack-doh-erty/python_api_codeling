import csv
from io import StringIO

from django.db.models import QuerySet
from django.http import HttpResponse

from common.filters import BarksFilter, apply_ordering
from core.models import BarkModel, DogUserModel
from api_v2.logic.exceptions import DuplicateResourceError, ResourceNotFoundError


def handle_export_top_barks_csv(user: DogUserModel) -> HttpResponse:
    """
    Handle the logic for exporting user's top 10 sniffed barks as CSV.
    Returns an HttpResponse with CSV content.
    """
    top_barks = (
        BarkModel.objects.filter(user=user, sniff_count__gt=0)
        .order_by("-sniff_count")[:10]
    )

    csv_data = StringIO()
    writer = csv.writer(csv_data)
    writer.writerow(["Message", "Sniff Count", "Created At", "Username"])

    for bark in top_barks:
        writer.writerow(
            [bark.message, bark.sniff_count, str(bark.created_at), user.username]
        )

    response = HttpResponse(csv_data.getvalue(), content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="top_barks.csv"'
    return response


def handle_barks_list(filters: BarksFilter) -> QuerySet[BarkModel]:
    """Return all barks with their users loaded."""
    objs = BarkModel.objects.select_related("user").all()
    results = filters.filter(objs)

    if filters.trending:
        return results.order_by("-sniff_count")

    return apply_ordering(results, filters.order_by)


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
