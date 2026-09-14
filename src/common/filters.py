from typing import Any, Optional

from django.core.exceptions import FieldDoesNotExist
from django.db.models import Q, QuerySet
from django.utils import timezone
from ninja import Field, FilterSchema


class UsersFilter(FilterSchema):
    """Filter schema for user endpoints."""

    favorite_toy: Optional[str] = Field(None, q="favorite_toy__icontains")
    username: Optional[str] = Field(None, q="username__icontains")
    search: Optional[str] = Field(
        None,
        q=["favorite_toy__icontains", "username__icontains"],
    )
    order_by: Optional[str] = None

    def filter_order_by(self, value: str) -> Q:
            """Filter for ordering barks"""
            return Q()


class BarksFilter(FilterSchema):
    """Filter schema for bark endpoints."""

    message: Optional[str] = Field(None, q="message__icontains")
    trending: Optional[bool] = None
    order_by: Optional[str] = None

    def filter_trending(self, value: bool) -> Q:
        """Filter for trending barks"""
        if not value:
            return Q()

        return Q(
            created_at__gte=timezone.now() - timezone.timedelta(days=1),
            sniff_count__gte=1,
        )

    def filter_order_by(self, value: str) -> Q:
        """Filter for ordering barks"""
        return Q()


def apply_ordering(
    queryset: QuerySet,
    order_by: Optional[str],
    model_class: Any = None,
) -> QuerySet:
    """
    Apply ordering to a queryset based on an order_by parameter.

    Args:
        queryset: The Django queryset to order
        order_by: The field to order by (with optional - prefix for descending)
        model_class: Optional model class used to validate the ordering field

    Returns:
        The ordered queryset
    """
    if not order_by:
        return queryset

    model_class = model_class or queryset.model
    field_name = order_by.removeprefix("-")
    try:
        model_class._meta.get_field(field_name)
    except FieldDoesNotExist:
        return queryset

    return queryset.order_by(order_by)
