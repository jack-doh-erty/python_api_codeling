from ninja import Schema
from api_v2.schemas.bark_schemas import BarkSchemaOut
from uuid import UUID


class SniffCreateSchemaIn(Schema):
    """Schema for creating a sniff"""

    bark_id: UUID


class SniffSchemaOut(BarkSchemaOut):
    """Schema for sniff responses"""

    pass
