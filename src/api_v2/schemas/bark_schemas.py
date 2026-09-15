from ninja import ModelSchema, Schema

from api_v2.schemas.user_schemas import DogUserSchemaOut
from core.models import BarkModel
from pydantic import field_validator


class BarkCsvExportSchema(Schema):
    """Schema for CSV export data"""

    message: str
    sniff_count: int
    created_at: str
    username: str


class BarkSchemaOut(ModelSchema):
    """Schema for bark responses"""

    user: DogUserSchemaOut
    created_time: str
    created_date: str
    updated_time: str
    updated_date: str

    class Meta:
        model = BarkModel
        fields = ["id", "message", "sniff_count"]

    @staticmethod
    def resolve_created_time(obj):
        """Resolve created time in format 06:12pm from created_at field"""
        return obj.created_at.strftime("%I:%M %p")

    @staticmethod
    def resolve_created_date(obj):
        """Resolve created date in format 15Jan25 from created_at field."""
        return obj.created_at.strftime("%d%b%y")

    @staticmethod
    def resolve_updated_time(obj):
        """Resolve updated time from the updated_at field."""
        return obj.updated_at.strftime("%I:%M %p")

    @staticmethod
    def resolve_updated_date(obj):
        """Resolve updated date from the updated_at field."""
        return obj.updated_at.strftime("%d%b%y")


class BarkCreateUpdateSchemaIn(ModelSchema):
    """Schema for creating or updating a bark."""

    message: str

    @field_validator('message')
    @classmethod
    def validate_message_not_empty(cls, v: str) -> str:
        """Ensure message isn't just whitespace"""
        if not v.strip():
            raise ValueError("Message cannot be empty or just whitespace")
        return v

    class Meta:
        model = BarkModel
        fields = ["message"]
