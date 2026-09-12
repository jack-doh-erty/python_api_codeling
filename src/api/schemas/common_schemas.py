from ninja import Schema


class ErrorSchemaOut(Schema):
    """Schema for error responses"""

    error: str
