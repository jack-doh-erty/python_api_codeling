import base64
import json
from typing import Any, Optional

from django.http import HttpRequest
from ninja import Schema
from ninja.pagination import PaginationBase


class SkipPagination(PaginationBase):
    """
    Custom pagination class that allows skipping a number of items
    and specifying the number of items per page.
    """

    class Input(Schema):
        skip: int = 0
        per_page: int = 5

    class Output(Schema):
        items: list[Any]
        total: int
        pages: int
        per_page: int
        skip: int
        next: Optional[str] = None
        previous: Optional[str] = None

    def paginate_queryset(self, queryset, pagination: Input, **params):
        skip = pagination.skip
        per_page = pagination.per_page
        count = queryset.count()

        request: HttpRequest = params.get("request")
        base_url = self._get_base_url(request)

        next_link = None
        if skip + per_page < count:
            next_link = f"{base_url}?skip={skip + per_page}&per_page={per_page}"

        previous_link = None
        if skip > 0:
            previous_skip = max(skip - per_page, 0)
            previous_link = (
                f"{base_url}?skip={previous_skip}&per_page={per_page}"
            )

        return {
            "items": queryset[skip : skip + per_page],
            "total": count,
            "pages": (count + per_page - 1) // per_page,
            "per_page": per_page,
            "skip": skip,
            "next": next_link,
            "previous": previous_link,
        }

    def _get_base_url(self, request):
        """Build the base URL without query parameters."""
        if not request:
            return ""

        path = request.path
        scheme = "https" if request.is_secure() else "http"
        host = request.get_host()
        return f"{scheme}://{host}{path}"


class TimestampCursorPagination(PaginationBase):
    """
    Cursor pagination using timestamps.
    """

    class Input(Schema):
        cursor: Optional[str] = None
        limit: int = 10

    class Output(Schema):
        items: list[Any]
        count: int
        next: Optional[str] = None
        next_cursor: Optional[str] = None
        previous: Optional[str] = None
        previous_cursor: Optional[str] = None

    def paginate_queryset(self, queryset, pagination: Input, **params):
        limit = min(pagination.limit, 100)
        cursor = pagination.cursor

        request: HttpRequest = params.get("request")
        base_url = self._get_base_url(request)

        queryset = queryset.order_by("-created_at")
        count = queryset.count()

        filter_kwargs = {}
        if cursor:
            decoded = self.decode_cursor(cursor)
            if decoded is not None:
                timestamp = decoded.get("timestamp")
                if timestamp is not None:
                    filter_kwargs["created_at__lt"] = timestamp

        results = list(queryset.filter(**filter_kwargs)[: limit + 1])

        has_next = len(results) > limit
        if has_next:
            results.pop()

        next_cursor = None
        if has_next and results:
            next_timestamp = results[-1].created_at.isoformat()
            next_cursor = self.encode_cursor({"timestamp": next_timestamp})

        previous_cursor = None
        if results and cursor:
            first_timestamp = results[0].created_at.isoformat()
            prev_items = list(
                queryset.filter(created_at__gt=first_timestamp)
                .order_by("created_at")[:limit]
            )

            if prev_items:
                oldest_prev_item = prev_items[-1].created_at.isoformat()
                previous_cursor = self.encode_cursor(
                    {"timestamp": oldest_prev_item}
                )

        return {
            "items": results,
            "count": count,
            "next": (
                f"{base_url}?cursor={next_cursor}&limit={limit}"
                if next_cursor
                else None
            ),
            "next_cursor": next_cursor,
            "previous": (
                f"{base_url}?cursor={previous_cursor}&limit={limit}"
                if previous_cursor
                else None
            ),
            "previous_cursor": previous_cursor,
        }

    def decode_cursor(self, cursor):
        """Decode the cursor data from a URL-safe string."""
        if not cursor:
            return None
        try:
            decoded = base64.b64decode(cursor.encode()).decode()
            return json.loads(decoded)
        except (ValueError, json.JSONDecodeError):
            return None

    def encode_cursor(self, data):
        """Encode the cursor data into a URL-safe string."""
        json_str = json.dumps(data)
        encoded = base64.b64encode(json_str.encode()).decode()
        return encoded

    def _get_base_url(self, request):
        """Build the base URL without query parameters."""
        if not request:
            return ""

        path = request.path
        scheme = "https" if request.is_secure() else "http"
        host = request.get_host()
        return f"{scheme}://{host}{path}"
